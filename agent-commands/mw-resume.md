---
description: "Resume a saved workflow task from any coding-agent interface."
argument-hint: "TASK"
disable-model-invocation: true
---

# /mw-resume

Arguments: `$ARGUMENTS`

Read `~/workflow/docs/QUICKSTART.md` and the feature-pipeline skill.
Use the supplied task ID; if absent, run `~/workflow/bin/mw list` and ask which
existing task to resume. Do not pick an unrelated task or create a replacement.
Inspect `mw status TASK`. Continue `mw run TASK --once` while gates pass.
For manual handoff use `mw next TASK --tool manual` and record the specified
structured result; disclose substitutions and preserve independent high-risk
review. Configure real executable checks before verification. Diagnose failures
before bounded repair. Never reset budgets or skip gates to force completion.
Do not commit/push unless requested after the runner reports ready.
