"""Offline integration tests using real Git checkouts and deterministic fake CLIs."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MW = ROOT / "bin/mw"

FAKE = r'''#!/usr/bin/env python3
import json, os, re, sys, time
from pathlib import Path
prompt = sys.argv[-1]
stage = re.search(r'ONE workflow stage: (\w+)', prompt).group(1)
before = re.search(r'"fingerprint": "([0-9a-f]+)"', prompt.split('Write exactly one JSON object to ')[-1]).group(1)
result = Path(re.search(r'Write exactly one JSON object to (.+) with these fields:', prompt).group(1))
if os.environ.get('SLOW_STAGE') == stage:
    time.sleep(5)
if os.environ.get('EXIT_STAGE') == stage:
    sys.exit(9)
if stage == 'implement' or os.environ.get('EDIT_STAGE') == stage:
    Path('source.txt').write_text('implemented\n')
verdict = 'APPROVE' if stage == 'review' else 'PASS'
if os.environ.get('FAIL_STAGE') == stage:
    verdict = 'REQUEST_CHANGES' if stage == 'review' else 'FAIL'
result.write_text(json.dumps({'stage':stage, 'fingerprint':before, 'verdict':verdict,
    'summary':'Offline fake CLI: ' + Path(sys.argv[0]).name,
    'acceptance_criteria':['Source contains implemented behavior'], 'findings':[]}))
print('Fake stage completed:', stage)
'''


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.repo = self.base / "product"
        self.repo.mkdir()
        self.bin = self.base / "bin"
        self.bin.mkdir()
        for tool in ("codex", "agent", "claude", "opencode", "dsh"):
            path = self.bin / tool
            path.write_text(FAKE)
            path.chmod(0o755)
        self.env = {**os.environ, "HOME": str(self.home),
                    "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "XDG_STATE_HOME": str(self.home / ".local/state"),
                    "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
                    "DEEPSEEK_API_KEY": "offline-placeholder"}
        for key in ("EDIT_STAGE", "EXIT_STAGE", "SLOW_STAGE", "FAIL_STAGE"):
            self.env.pop(key, None)
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        (self.repo / "source.txt").write_text("original\n")
        (self.repo / ".gitignore").write_text("build/\n")
        self.git("add", ".")
        self.git("commit", "-qm", "Initial")
        self.check = json.dumps([sys.executable, "-c",
                                "from pathlib import Path; assert Path('source.txt').read_text() == 'implemented\\n'"])

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def cli(self, *args, ok=True):
        p = subprocess.run([sys.executable, str(MW), *args], cwd=self.repo,
                           env=self.env, capture_output=True, text=True)
        if ok:
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        else:
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def start(self, *args):
        p = self.cli("start", "--brief", "Fix source behavior", "--check", self.check, *args)
        return p.stdout.splitlines()[0]

    def folder(self, task):
        return self.home / ".local/state/workflow/tasks" / task

    def data(self, task):
        return json.loads((self.folder(task) / "task.json").read_text())

    def override(self, data):
        path = self.home / ".config/workflow/config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    def test_low_risk_complete_and_no_commit(self):
        head = self.git("rev-parse", "HEAD").stdout
        task = self.start("--risk", "low")
        self.cli("run", task)
        data = self.data(task)
        self.assertTrue(data["ready"])
        self.assertEqual(data["stages"], ["implement", "precheck", "review", "verify"])
        self.assertEqual(data["attempts"], 2)
        self.assertEqual(self.git("rev-parse", "HEAD").stdout, head)
        self.assertTrue(any(x["event"] == "check" and x["exit_code"] == 0 for x in data["history"]))

    def test_high_risk_routes_plan_and_review_to_codex(self):
        task = self.start("--risk", "high")
        self.cli("run", task)
        records = [x for x in self.data(task)["history"] if x["event"] == "stage"]
        self.assertEqual([x["role"]["tool"] for x in records], ["codex", "deepseek", "cursor", "codex"])
        self.assertTrue(self.data(task)["criteria"])

    def test_ui_gate_cannot_be_skipped(self):
        task = self.start("--flow", "ship-change")
        p = self.cli("run", task, ok=False)
        self.assertIn("UI gate required", p.stderr)
        self.assertFalse(self.data(task)["ready"])
        self.assertEqual(self.data(task)["attempts"], 0)
        self.cli("checks", task, "--ui-check", self.check)
        self.cli("run", task)
        self.assertTrue(self.data(task)["ready"])

    def test_checkout_edits_invalidate_ready_and_untracked_files(self):
        task = self.start("--risk", "low")
        self.cli("run", task)
        (self.repo / "new-file.txt").write_text("new work")
        self.cli("status", task)
        self.assertFalse(self.data(task)["ready"])
        self.assertEqual(self.data(task)["index"], 0)

    def test_index_changes_invalidate_ready(self):
        task = self.start("--risk", "low")
        self.cli("run", task)
        self.git("add", "source.txt")
        self.cli("status", task)
        self.assertFalse(self.data(task)["ready"])

    def test_ignored_build_output_does_not_invalidate(self):
        task = self.start("--risk", "low")
        self.cli("run", task)
        (self.repo / "build").mkdir()
        (self.repo / "build/generated.txt").write_text("artifact")
        self.cli("status", task)
        self.assertTrue(self.data(task)["ready"])

    def test_readonly_reviewer_changes_rejected(self):
        task = self.start("--flow", "review-update", "--ui-check", json.dumps([sys.executable, "-c", "pass"]))
        self.cli("checks", task, "--check", json.dumps([sys.executable, "-c", "pass"]))
        self.env["EDIT_STAGE"] = "review"
        p = self.cli("run", task, ok=False)
        self.assertIn("Read-only stage", p.stderr)
        self.assertFalse(self.data(task)["ready"])

    def test_failing_check_stops_and_repair_is_bounded(self):
        self.override({"limits": {"max_repairs": 1}})
        task = self.start("--risk", "low", "--check", json.dumps([sys.executable, "-c", "raise SystemExit(7)"]))
        self.cli("run", task, ok=False)
        self.assertFalse(self.data(task)["ready"])
        self.cli("run", task, ok=False)
        self.cli("repair", task, "--reason", "Diagnosed failure")
        self.assertEqual(self.data(task)["index"], 0)
        self.cli("repair", task, "--reason", "Must not loop", ok=False)

    def test_attempt_limit_allows_final_attempt_execution(self):
        self.override({"limits": {"max_attempts": 2}})
        task = self.start("--risk", "low")
        self.cli("run", task)
        self.assertTrue(self.data(task)["ready"])

    def test_attempt_limit_blocks_extra_stage(self):
        self.override({"limits": {"max_attempts": 1}})
        task = self.start("--risk", "low")
        self.cli("run", task, "--once")
        p = self.cli("run", task, ok=False)
        self.assertIn("Attempt limit", p.stderr)

    def test_estimated_cap_requires_estimates(self):
        self.override({"limits": {"max_estimated_usd": 1}})
        task = self.start("--risk", "low")
        self.assertIn("requires estimated_cost_usd", self.cli("run", task, ok=False).stderr)

    def test_estimated_cap_reservation(self):
        self.override({"limits": {"max_estimated_usd": 1}, "roles": {
            "implement": {"estimated_cost_usd": 0.6}, "review": {"estimated_cost_usd": 0.6}}})
        task = self.start("--risk", "low")
        self.assertIn("cap would be exceeded", self.cli("run", task, ok=False).stderr)
        self.assertEqual(self.data(task)["estimated_usd"], 0.6)

    def test_agent_error_does_not_fallback_or_advance(self):
        task = self.start("--risk", "low")
        self.env["EXIT_STAGE"] = "implement"
        self.cli("run", task, ok=False)
        data = self.data(task)
        self.assertEqual(data["index"], 0)
        self.assertEqual(data["attempts"], 1)
        self.assertTrue(data["blocked"])

    def test_failed_high_risk_plan_cannot_be_skipped_by_repair(self):
        task = self.start("--risk", "high")
        self.env["FAIL_STAGE"] = "plan"
        self.cli("run", task, ok=False)
        self.cli("repair", task, "--reason", "Clarified requirements")
        self.assertEqual(self.data(task)["index"], 0)
        self.assertEqual(self.data(task)["stages"][0], "plan")

    def test_timeout_preserves_state(self):
        self.override({"limits": {"process_timeout_seconds": 0.1}})
        task = self.start("--risk", "low")
        self.env["SLOW_STAGE"] = "implement"
        self.cli("run", task, ok=False)
        self.assertTrue(self.data(task)["blocked"])
        self.assertGreater(self.data(task)["active_seconds"], 0)

    def test_manual_handoff_and_stale_result_rejection(self):
        task = self.start("--risk", "low")
        self.cli("next", task, "--tool", "manual")
        flight = self.data(task)["flight"]
        result = self.folder(task) / "manual.json"
        value = {"stage": "implement", "fingerprint": "stale", "verdict": "PASS",
                 "summary": "manual model", "acceptance_criteria": ["Behavior"]}
        result.write_text(json.dumps(value))
        self.cli("record", task, "--result", str(result), ok=False)
        value["fingerprint"] = flight["before"]
        result.write_text(json.dumps(value))
        self.cli("record", task, "--result", str(result))
        self.assertEqual(self.data(task)["index"], 1)
        self.assertFalse(self.data(task)["ready"])

    def test_verify_requires_review_and_real_checks(self):
        task = self.start("--risk", "low")
        self.cli("check", task, ok=False)
        self.override({"checks": []})
        p = self.cli("start", "--brief", "No checks", "--risk", "low")
        task = p.stdout.splitlines()[0]
        self.assertIn("No deterministic checks", self.cli("run", task, ok=False).stderr)

    def test_checks_that_modify_source_invalidate_review(self):
        edit = json.dumps([sys.executable, "-c", "from pathlib import Path; Path('source.txt').write_text('test edit')"])
        task = self.start("--risk", "low", "--check", edit)
        self.assertIn("modified the checkout", self.cli("run", task, ok=False).stderr)
        self.assertEqual(self.data(task)["index"], 0)
        self.assertFalse(self.data(task)["ready"])

    def test_config_snapshot_and_tool_override(self):
        task = self.start("--risk", "low")
        self.override({"roles": {"implement": {"tool": "manual"}}})
        self.cli("run", task, "--once", "--tool", "opencode")
        data = self.data(task)
        result = next(x for x in data["history"] if x["event"] == "stage")
        self.assertEqual(result["role"], {"tool": "opencode", "model": ""})
        self.assertEqual(data["config"]["roles"]["implement"]["tool"], "deepseek")

    def test_dsh_profile_adapter(self):
        task = self.start("--risk", "low")
        self.cli("run", task, "--once", "--tool", "dsh")
        self.assertEqual(self.data(task)["index"], 1)

    def test_medium_routine_task_uses_two_agent_stages(self):
        task = self.start("--risk", "medium")
        self.cli("run", task)
        data = self.data(task)
        self.assertNotIn("test", data["stages"])
        self.assertEqual(data["attempts"], 2)
        self.assertTrue(data["ready"])

    def test_separate_test_stage_remains_configurable(self):
        self.override({"routing": {"separate_test_risks": ["medium", "high"]}})
        task = self.start("--risk", "medium")
        self.cli("run", task)
        self.assertEqual(self.data(task)["attempts"], 3)
        self.assertTrue(self.data(task)["ready"])

    def test_previously_saved_tasks_keep_their_original_stages(self):
        task = self.start("--risk", "low")
        data = self.data(task)
        data["stages"].remove("precheck")
        data["config"].pop("routing")
        (self.folder(task) / "task.json").write_text(json.dumps(data))
        self.cli("run", task)
        self.assertTrue(self.data(task)["ready"])
        self.assertNotIn("precheck", self.data(task)["stages"])

    def test_failed_precheck_avoids_review_launch(self):
        task = self.start("--risk", "medium", "--check", json.dumps([sys.executable, "-c", "raise SystemExit(2)"]))
        self.cli("run", task, ok=False)
        data = self.data(task)
        self.assertEqual(data["attempts"], 1)
        self.assertFalse(any(x.get("stage") == "review" for x in data["history"]))
        self.assertFalse(data["ready"])

    def test_precheck_does_not_replace_final_verification(self):
        task = self.start("--risk", "low")
        self.cli("run", task, "--once")
        self.cli("check", task)
        self.assertFalse(self.data(task)["ready"])
        self.cli("run", task)
        checks = [x for x in self.data(task)["history"] if x["event"] == "check"]
        self.assertEqual([x["stage"] for x in checks], ["precheck", "verify"])

    def test_second_repair_escalates_implementation(self):
        task = self.start("--risk", "medium")
        self.env["FAIL_STAGE"] = "implement"
        for number in range(2):
            self.cli("run", task, ok=False)
            self.cli("repair", task, "--reason", f"Diagnosed attempt {number + 1}")
        self.env.pop("FAIL_STAGE")
        self.cli("run", task)
        models = [x["role"]["model"] for x in self.data(task)["history"]
                  if x["event"] == "execution" and x["stage"] == "implement"]
        self.assertEqual(models, ["deepseek-flash", "deepseek-flash", "deepseek-v4-pro"])

    def test_metrics_distinguish_estimates_from_reported_billing(self):
        task = self.start("--risk", "medium")
        self.assertIsNone(json.loads(self.cli("metrics", task).stdout)["user_reported_usd"])
        self.cli("cost", task, "--usd", "0.12", "--provider", "deepseek", "--reference", "usage-1")
        self.cli("cost", task, "--usd", "0.12", "--provider", "deepseek", "--reference", "usage-1", ok=False)
        self.cli("cost", task, "--usd", "nan", "--provider", "deepseek", "--reference", "invalid", ok=False)
        self.cli("run", task)
        metrics = json.loads(self.cli("metrics", task).stdout)
        self.assertEqual(metrics["user_reported_usd"], 0.12)
        self.assertEqual(metrics["cli_launches"], 2)
        self.assertEqual(metrics["review_launches"], 1)
        self.assertFalse(metrics["billing_verified"])

    def test_invalid_configuration_is_reported_cleanly(self):
        self.override({"roles": []})
        p = self.cli("config", ok=False)
        self.assertIn("roles and limits must be JSON objects", p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_shell_metacharacters_are_data(self):
        p = self.cli("start", "--brief", "Fix `touch PWNED` $(touch PWNED) ; quotes ' \"", "--risk", "low", "--check", self.check)
        task = p.stdout.splitlines()[0]
        self.cli("run", task)
        self.assertFalse((self.repo / "PWNED").exists())

    def test_single_checkout_operation_lock(self):
        import fcntl
        import hashlib
        folder = self.home / ".local/state/workflow/locks"
        folder.mkdir(parents=True)
        lock = folder / (hashlib.sha256(str(self.repo.resolve()).encode()).hexdigest() + ".lock")
        with lock.open("a+") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn("Another workflow operation", self.cli("start", "--brief", "Busy", ok=False).stderr)

    def test_installer_idempotence_native_adapters_and_backups(self):
        zshrc = self.home / ".zshrc"
        zshrc.write_text("# unrelated private configuration\nexport KEEP_ME=yes\n")
        cmd = ["zsh", str(ROOT / "install.sh"), "--home", str(self.home)]
        first = subprocess.run(cmd, env=self.env, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        second = subprocess.run(cmd, env=self.env, capture_output=True, text=True)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("Updated 0 files/links", second.stdout)
        self.assertIn("export KEEP_ME=yes", zshrc.read_text())
        self.assertEqual(zshrc.read_text().count("# >>> workflow home >>>"), 1)
        self.assertTrue(list((self.home / ".local/state/workflow/install-backups").glob("**/.zshrc")))
        dsh = (self.home / ".dsh/skills/mw-ship-change.md").read_text()
        self.assertIn("user-invocable: true", dsh)
        self.assertNotIn("$ARGUMENTS", dsh)
        opencode = (self.home / ".config/opencode/commands/mw-ship-change.md").read_text()
        self.assertIn("$ARGUMENTS", opencode)
        self.assertNotIn("disable-model-invocation:", opencode)
        self.assertTrue((self.home / ".agents/skills/workflow/SKILL.md").exists())
        self.assertFalse((self.repo / "AGENTS.md").exists())
        link = self.home / ".local/bin/mw"
        p = subprocess.run([str(link), "list"], env=self.env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        alias = self.home / ".local/bin/commit-change"
        p = subprocess.run([str(alias), "--pro", "Fix source behavior"], cwd=self.repo,
                           env=self.env, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(self.data(p.stdout.splitlines()[0])["pro"])


if __name__ == "__main__":
    unittest.main()
