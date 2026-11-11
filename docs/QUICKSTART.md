# Use the same workflow everywhere

Install or refresh: `~/workflow/install.sh`, then open a new agent session.
Check tools with `~/workflow/bin/mw doctor`. Git and Python 3.10+ are required.
You can use this from any Git checkout; Orca is optional.

## From an agent UI

Cursor, Claude Code, OpenCode, DeepSeek Harness TUI or web UI:

```text
/mw start Fix the empty-state behavior on the events list
/mw-ship-from-spec Add event filtering with the supplied requirements
/mw-commit-change Fix date serialization without changing UI
/mw-resume TASK_ID
```

The command asks the current agent to use the shared runner. It does not change
the UI's current model. Configured cross-tool stages run through child CLIs.
Your existing UI remains the coordinator and receives saved results.

Codex CLI or Codex app uses a skill instead of pretending to support custom /mw:

```text
$workflow start Fix the empty-state behavior on the events list
$workflow ship-from-spec Add event filtering with the supplied requirements
$workflow resume TASK_ID
```

Start Codex in the target checkout (`codex`), then enter that prompt. The skill
is installed in ~/.agents/skills/workflow. If missing, restart Codex. Native
commands/skills are prompts, not proof that a model ran or a test passed.

## From a terminal

```bash
cd /path/to/product-checkout
mw start --risk medium --brief "Fix date serialization" \
  --check '["./gradlew", ":library:events:test"]'
# Copy the printed task ID into subsequent commands:
mw run TASK_ID --once
mw status TASK_ID
mw resume TASK_ID
```

Replace the Gradle example with real commands for your project. `run`/`resume`
execute remaining configured stages until complete or blocked; --once runs one
stage. Neither creates a commit. Console output points to saved agent/check logs.
No automatic model fallback runs after a failure.

Legacy names remain: `ship-from-spec "brief"`, `ship-change "brief"`,
`commit-change "brief"`, `review-update "brief"`. They now create a saved task
and print its ID; continue with `mw run TASK_ID`. --pro selects the stronger
implementation role. `myworkflow` is a menu; `myworkflow help` shows this guide.
`review-pr` and `/mw-review-pr` retain their separate review-only behavior.

## Routing and verification

| Task | Stages |
|---|---|
| Adaptive low risk | implement → precheck → review → verify |
| Adaptive medium non-UI | implement → precheck → review → verify |
| Adaptive high risk | plan → implement → test/refactor → precheck → review → verify |
| ship-from-spec | plan → implement → test → precheck → review → verify, UI required |
| ship-change | implement → test → precheck → review → verify, UI required |
| commit-change | adaptive stages, no UI requirement unless --ui supplied |
| review-update | precheck → review → verify, UI required |

High risk adds a plan even for legacy flows; review-update checks and reviews already written
work. UI tasks retain separate test authoring. Configure routing.separate_test_risks
to add that stage to other risk levels. Choose high risk for permissions, payments, migrations, public contracts,
and major architectural uncertainty. Adaptive tasks require --ui for UI changes.
Risk classification is a caller/agent responsibility, not an infallible classifier.

Defaults: Codex planning, DeepSeek implementation, Cursor Auto test/refactor and
routine review, Codex high-risk review. Routine non-UI tasks avoid separate planning and test-authoring calls, but still
require independent review and executable checks. The implementer authors needed
regression tests. High-risk work retains stronger planning and test authoring.

Configure checks before launching paid stages, with argument arrays (no shell
evaluation). Missing regular or required UI checks block mw run before spending:

```bash
mw checks TASK_ID --check '["./gradlew", "test"]' \
  --ui-check '["maestro", "test", "/absolute/path/to/related-flows"]'
# At precheck or final verification:
mw check TASK_ID
```

--check replaces that task's regular checks; --ui-check replaces UI checks.
UI-required flows stop until UI commands are provided and succeed. Agents should
select meaningful coverage; a successful no-op command is not useful evidence.
Only runner-executed commands release the final gate. Regular checks run before
review to catch obvious failures cheaply, and run again after review for fresh
release evidence. Precheck never grants readiness; UI checks run at final verify. Tests that alter tracked or
nonignored files invalidate review; configure generated outputs as Git-ignored.

Review/test evidence is bound to HEAD, index and checkout contents, including
nonignored untracked files. Later checkout edits invalidate readiness. Ignored
files and external services/devices are outside that fingerprint. Keep externally
stored Maestro flows stable during verification; rerun checks after changing them.

## Handoff without launching another CLI

Useful when a UI cannot launch a child agent, or to use the current subscription:

```bash
mw next TASK_ID --tool manual
# The current agent follows that one stage prompt and writes its result file.
mw record TASK_ID --result /absolute/path/printed-by-the-prompt.result.json
mw status TASK_ID
```

The prompt includes criteria, recent handoffs, the current fingerprint and exact
JSON schema. Record the actual tool/model in the summary. Manual mode uses the
current model; it does not implement the configured provider routing. Arrange an
independent external or human review for high-risk work. Plan/review are logically
read-only: checkout edits are detected and rejected, not rolled back automatically.
The runner is a coordination/gating tool, not a security sandbox.

To continue in another UI, use /mw-resume TASK_ID or $workflow resume TASK_ID.
Do not run two writers in the same checkout. The runner locks its own operations,
but cannot lock unrelated editors or agents.

## Failures and budgets

```bash
mw status TASK_ID
# Inspect the saved log/result, diagnose, then explicitly start a repair:
mw repair TASK_ID --reason "The null timestamp case fails; fix the parser"
mw run TASK_ID --once
```

Repair returns to implementation (precheck for existing-code review-update) and
invalidates prior approval. A second diagnosed repair uses implement_high;
routing.escalate_after_repairs configures this threshold. Existing saved tasks
retain their captured routing and stages. Default limits: 12 stage attempts, 2 repairs, 60 minutes
of runner-controlled subprocess execution, 15 minutes per process. Manual chat
time is not measured. Checks consume the same active execution budget. Budgets
are snapshotted at task creation; restarting a UI does not reset them.

Tool failures preserve logs and pending state. You may record a valid completed
result after interruption, or diagnose and repair. Never retry blindly. To select
another execution tool on the next attempt, `mw run TASK_ID --once --tool codex`
(also cursor, deepseek, opencode, dsh). A tool override uses that tool's default
model because model identifiers are not portable. Complete or repair a pending
attempt before switching. `mw next` reprints an existing pending prompt.

## Configure models and costs

Defaults: ~/workflow/config/default.json. Optional user overrides:
~/.config/workflow/config.json (respects XDG_CONFIG_HOME). `mw config` prints the
effective settings. Partial JSON overrides merge with defaults. Example:

```json
{
  "version": 1,
  "roles": {
    "plan": {"tool": "codex", "model": ""},
    "implement": {"tool": "deepseek", "model": "deepseek-flash"},
    "test": {"tool": "cursor", "model": "auto"},
    "review": {"tool": "cursor", "model": "auto"}
  },
  "limits": {"max_attempts": 12, "max_repairs": 2},
  "checks": [],
  "ui_checks": []
}
```

An empty model inherits the CLI's configured default; it does not select a named
premium model. DeepSeek identifiers above preserve your existing setup; verify
availability in your account. Available tools are codex, cursor, deepseek (Claude
Code using DeepSeek's endpoint), opencode, dsh (its configured headless profile),
and manual. OpenCode models use its provider/model syntax. Keep dsh.model empty;
model selection belongs to its profile. Adapters keep normal CLI permissions;
they do not enable blanket auto-approval. A permission/trust denial stops the
stage for inspection. Authenticate/trust each tool normally before unattended use.

Export DEEPSEEK_API_KEY in your private environment. No secrets are read from
project files, logged, or installed. Provider credentials and model access are
managed by the respective tools, not the workflow installer.

Set limits.max_estimated_usd and each role's estimated_cost_usd to enforce a
reservation-based *estimated* spend ceiling. Missing estimates block execution
under that ceiling. This does not measure billing or enforce a hard provider USD
limit; use provider spend controls for that. Subscription quotas and API charges
are separate. `mw status` shows attempts, estimated spend and active seconds.

Task JSON, prompts, structured results and logs are stored in
~/.local/state/workflow/tasks/TASK_ID (respects XDG_STATE_HOME). The config snapshot
and history support comparisons of total attempts, repairs, execution time and
acceptance. Actual billing, human effort and escaped defects require external
measurement; no savings claim is built in. To attach non-overlapping usage amounts
from provider dashboards to a task:

```bash
mw cost TASK_ID --provider deepseek --reference usage-record-123 --usd 0.12
mw metrics TASK_ID
```

Amounts are user-reported, not independently verified billing. Duplicate
provider/reference pairs are rejected. Include every relevant provider for a
complete total; fixed subscription allocation and human time remain separate.
Metrics report CLI stage launches (not internal model/tool calls), repairs,
failed prechecks, active execution time, configured estimates and reported USD.
Compare these on equivalent tasks with the same acceptance criteria and checks.

## Installation locations and compatibility

- Cursor/Claude: home commands/mw*.md and feature-pipeline knowledge skill.
- OpenCode: ~/.config/opencode/commands/mw*.md and skills/feature-pipeline.
- DeepSeek Harness: ~/.dsh/skills/mw*.md, user-invocable flat skills for TUI/web.
- Codex: ~/.agents/skills/workflow plus feature-pipeline knowledge skill.
- Terminal: ~/.local/bin links and the marked WORKFLOW_HOME/PATH block in .zshrc.

The installer preserves unrelated files and backs up replaced files under
~/.local/state/workflow/install-backups. Reinstall after editing this project.
Use --no-shell to leave .zshrc unchanged. No product-root instruction files are
created. Existing open UIs may need a new session to reload commands/skills.

Sources checked for integration behavior:
[Codex skills](https://learn.chatgpt.com/docs/build-skills) and
[OpenCode commands](https://opencode.ai/docs/commands/), plus installed CLI help
for Codex, Cursor, OpenCode and DeepSeek Harness. Discovery/install checks do not
prove provider authentication or a real product's UI tests pass.
