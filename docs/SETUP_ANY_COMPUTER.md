# Setup on any computer

1. Copy this entire workflow folder to `~/workflow` (another location also works).
2. Install Python 3.10+, Git and zsh. The runner supports macOS/Linux.
3. Install/authenticate the CLIs used by your configured roles: Codex (`codex`),
   Cursor (`agent`), Claude Code (`claude`) for the DeepSeek adapter. OpenCode
   (`opencode`) and DeepSeek Harness (`dsh`) are optional alternative adapters/UIs.
4. Export DEEPSEEK_API_KEY through your private environment when using that adapter.
   Do not put secrets in this project. Subscription access and API billing differ.
5. Run `zsh ~/workflow/install.sh`, then start a new terminal/agent session.
   The installer updates only its marked PATH block in .zshrc; `--no-shell` leaves
   shell configuration alone. Replaced home files are backed up.
6. Run `~/workflow/bin/mw doctor`. It checks binaries/configuration, not live auth.
7. Read [QUICKSTART.md](QUICKSTART.md) and start from a product Git checkout.

Orca is optional: its agent terminals use these same CLI/home integrations.
Maestro plus an emulator/device is required for mobile UI checks. Preserve your
existing Maestro library (often ~/Documents/Maestro). Configure project-specific
check command arrays at task start or with `mw checks TASK`.

Native entry points:

| Interface | Entry |
|---|---|
| Cursor / Claude / OpenCode / DeepSeek Harness TUI and web | `/mw`, `/mw-*`, `/mw-resume` |
| Codex CLI / app | `$workflow start BRIEF`, `$workflow resume TASK` |
| Any terminal | `mw`, `myworkflow`, existing flow aliases |

For OpenCode, commands are installed even if its config folder did not previously
exist; XDG_CONFIG_HOME is respected. Codex uses the documented user skills folder
~/.agents/skills. DeepSeek Harness retains the existing flat user-invocable skill
layout. Restart running sessions if they have cached discovery data.

Updates: edit this project, rerun install.sh, restart sessions. The installer does
not replace credentials, provider configurations, or unrelated skills/commands.
To move tasks to another machine, also transfer the private workflow state/config
folders and deliberately adjust checkout paths; this is not automatic cloud sync.
Keep logs private because they may contain source and command output.
