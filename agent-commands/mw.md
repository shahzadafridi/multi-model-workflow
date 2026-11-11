---
description: "Shared workflow menu: start, resume, inspect configuration or choose a /mw flow."
argument-hint: "[flow and brief|resume TASK|help]"
disable-model-invocation: true
---

# /mw

Arguments: `$ARGUMENTS`

Read `~/workflow/docs/QUICKSTART.md` and the feature-pipeline skill.
With no arguments, show the flow choices: adaptive start, ship-from-spec,
ship-change, commit-change, review-update, review-pr, resume existing task.
Do not launch a shell menu that waits for interactive input inside a UI tool.

With a named flow, read its `~/workflow/agent-commands/mw-*.md` instructions.
With `resume TASK`, follow mw-resume.md. With help, explain the available choices.
For a plain task brief or `start BRIEF`, classify risk and UI impact, create an
adaptive task via `mw start --risk LEVEL --brief BRIEF` (add --ui for UI changes),
and run configured stages with `mw run TASK --once` while gates succeed.
Use proper argument quoting. Show the task ID and routing. Define executable
checks before final verification. Read QUICKSTART for manual handoff if CLI
launching is unavailable. Do not silently replace an independent reviewer.
Commit/push only when explicitly requested after gates pass.
