---
description: "Implementation, review and checks without a required UI gate; shared, resumable task across tools."
argument-hint: "[--pro] [brief]"
disable-model-invocation: true
---

# /mw-commit-change

Arguments: `$ARGUMENTS`

Read `~/workflow/skills/feature-pipeline/SKILL.md` and
`~/workflow/docs/QUICKSTART.md`. Use the canonical runner; do not recreate
its stages from memory or treat this command as an untracked chat-only flow.

1. Interpret arguments as the task brief; --pro selects the configured stronger
   implementer. If no brief or prior task context exists, ask for the task.
2. Classify risk (low/medium/high) from impact and uncertainty. Create a task with
   `~/workflow/bin/mw start --flow commit-change --risk LEVEL --brief BRIEF`.
   Pass brief as one properly quoted argument. Add --pro when requested.
3. Save/show the returned task ID. Inspect the project and configure meaningful
   regular and required UI checks with `mw checks` before any paid stage.
   Run `mw run TASK --once`, inspect status, and repeat while stages succeed. Each stage uses its configured tool/model.
4. If this environment cannot launch a CLI, disclose it. Manual handoff uses
   `mw next TASK --tool manual`, performs that single stage, writes the JSON
   result path specified in the prompt, and records it via `mw record`.
   Identify the actual model in the handoff; retain independent high-risk review.
5. Configure meaningful executable checks using `mw checks`. Required UI flows
   need --ui-check commands, normally Maestro. Run `mw check` at precheck and final verification.
   Missing tools/devices or failed commands must stop the release gate.
6. On failure, inspect saved artifacts before bounded `mw repair`. Never silently
   skip review, UI gates, or substitute a model and claim independent review.
7. Report ready only after the runner says ready for the current checkout.
   Do not commit/push unless the user requested it. Commit messages contain no
   AI/tool names. Never put workflow/AI files into Android/MoSec project roots.

Resume the same task from another tool with `/mw-resume TASK` or
Codex `$workflow resume TASK`. Do not create a second task for a handoff.
