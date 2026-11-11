---
name: workflow
description: Start or resume the user's shared /mw coding workflow from Codex. Use when explicitly invoked with $workflow; accepts a flow and brief or an existing task ID.
---

Use `~/workflow/bin/mw`. Read `~/workflow/docs/QUICKSTART.md` for usage and
`~/workflow/skills/feature-pipeline/SKILL.md` for stage rules.

Arguments follow `$workflow` in the user's message:
- `ship-from-spec <brief>`: planned flow with UI gate.
- `ship-change <brief>`: implementation flow with UI gate.
- `commit-change <brief>`: no UI gate, still review and deterministic checks.
- `review-update <brief>`: existing implementation, review and UI verification.
- `start <brief>`: adaptive flow; classify risk and whether UI is affected.
- `resume <task-id>`: inspect status and continue the saved task.
- `review-pr <target>`: read `~/workflow/agent-commands/mw-review-pr.md`; review only.
- Empty arguments or `help`: summarize options; do not create an empty task.

Create tasks with `mw start` using separately quoted flow, risk, UI flag and brief.
Show the returned task ID, chosen risk and stages. Never interpolate raw user
text into shell code. By default run `mw run TASK --once`, inspect status, and
repeat while gates succeed. A stage agent must not recursively launch workflows.

If this environment cannot launch a CLI, disclose that limitation. Manual handoff:
`mw next TASK --tool manual`, perform only that stage, write the specified JSON
result, then `mw record TASK --result PATH`. Identify the actual model/tool in the
summary. Preserve independent high-risk review through an external reviewer or
human handoff; do not silently substitute yourself.

Set meaningful executable checks through `mw checks`, then use `mw check TASK`
at verification. Failures stop: inspect artifacts before bounded `mw repair`.
Report completion only when status says ready for the current checkout.
Commit/push remain explicit user actions.
