"""Install shared commands and skills with backups; safe to rerun."""
import argparse
import datetime as dt
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def install(home, update_shell=True):
    home = Path(home).expanduser().resolve()
    config_root = Path(os.environ.get("XDG_CONFIG_HOME", str(home / ".config")))
    state = Path(os.environ.get("XDG_STATE_HOME", str(home / ".local/state"))) / "workflow"
    backup = state / "install-backups" / dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    changes = []

    def preserve(path):
        if path.exists() or path.is_symlink():
            backup.mkdir(parents=True, exist_ok=True, mode=0o700)
            target = backup / str(path).lstrip("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            if path.is_symlink():
                target.symlink_to(os.readlink(path))
            else:
                shutil.copy2(path, target)

    def write(path, content):
        if path.is_file() and not path.is_symlink() and path.read_text() == content:
            return
        preserve(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            path.unlink()
        path.write_text(content)
        changes.append(str(path))

    def link(path, target):
        if path.is_symlink() and path.resolve() == target:
            return
        preserve(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() or path.is_symlink():
            path.unlink()
        path.symlink_to(target)
        changes.append(str(path))

    for source in (ROOT / "bin").iterdir():
        if source.is_file() and not source.name.endswith(".zsh"):
            source.chmod(source.stat().st_mode | 0o111)
            link(home / ".local/bin" / source.name, source)

    # .agents/skills is Codex's documented user-level discovery root.
    for skill in (ROOT / "skills").iterdir():
        source = skill / "SKILL.md"
        if not source.exists():
            continue
        roots = [home / ".agents/skills"] if skill.name == "workflow" else [
            home / ".agents/skills", home / ".cursor/skills", home / ".claude/skills",
            home / ".dsh/skills", config_root / "opencode/skills"]
        for dest in roots:
            write(dest / skill.name / "SKILL.md", source.read_text().replace("~/workflow", str(ROOT)))
            if skill.name == "workflow":
                write(dest / skill.name / "agents/openai.yaml",
                      'interface:\n  display_name: "My Workflow"\n  short_description: "Start or resume the shared coding workflow"\n'
                      'policy:\n  allow_implicit_invocation: false\n')

    for source in sorted((ROOT / "agent-commands").glob("mw*.md")):
        text = source.read_text().replace("~/workflow", str(ROOT))
        match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        header, body = match.groups()
        for dest in (home / ".cursor/commands", home / ".claude/commands"):
            write(dest / source.name, text)
        description = next(line for line in header.splitlines() if line.startswith("description:"))
        write(config_root / "opencode/commands" / source.name,
              f"---\n{description}\n---\n{body}")
        write(home / ".dsh/skills" / source.name,
              f"---\nname: {source.stem}\n{description}\nuser-invocable: true\n"
              f"disable-model-invocation: true\n---\n{body.replace('$ARGUMENTS', 'the text typed after this command')}")

    # Refresh only our marked block; preserve all other shell configuration.
    if update_shell:
        zshrc = home / ".zshrc"
        text = zshrc.read_text() if zshrc.exists() else ""
        start, end = "# >>> workflow home >>>", "# <<< workflow home <<<"
        quoted = str(ROOT).replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`")
        block = f'''{start}
export WORKFLOW_HOME="{quoted}"
export PATH="$WORKFLOW_HOME/bin:$HOME/.local/bin:$PATH"
{end}'''
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        updated = pattern.sub(lambda _: block, text) if pattern.search(text) else text.rstrip() + "\n\n" + block + "\n"
        write(zshrc, updated)

    print(f"Installed from: {ROOT}")
    print(f"Updated {len(changes)} files/links. Backups (when needed): {backup}")
    print("Cursor / Claude / OpenCode / DeepSeek Harness: /mw and /mw-* commands")
    print("Codex CLI / Codex app: $workflow (e.g. $workflow ship-change Add pagination)")
    print("Terminal: mw doctor; myworkflow help. Restart existing agent sessions if needed.")
    print("No authentication settings, provider defaults, or API keys were changed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=str(Path.home()), help="Alternate installation home (for testing)")
    parser.add_argument("--no-shell", action="store_true", help="Do not update the marked .zshrc block")
    args = parser.parse_args()
    install(args.home, not args.no_shell)
