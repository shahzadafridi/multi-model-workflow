---
name: feature-pipeline
description: Run the user's portable multi-model feature pipeline with saved handoffs, configurable OpenAI/DeepSeek/Cursor roles, review gates, and executable verification. Use for /mw flows and explicit workflow tasks across coding agents.
---

The canonical runner is `~/workflow/bin/mw`. Use one task ID across interfaces.
Commands: start, next, run, resume, record, check, checks, repair, status, list,
doctor. Read `~/workflow/docs/QUICKSTART.md` for usage.

## Routing

- Low risk: implement → review → verify.
- Medium: implement → test/refactor → review → verify.
- High: plan → implement → test/refactor → review → verify.
- ship-from-spec always includes plan and UI verification.
- ship-change always includes UI verification.
- commit-change omits UI verification, retains review and executable checks.
- review-update starts at review and requires UI verification.

Use high risk for authentication/authorization, payments, migrations, public
contracts, or substantial architectural uncertainty. For adaptive auto tasks,
add --ui when UI behavior is affected. Low risk does not waive a required UI gate.

Defaults: Codex plan, DeepSeek implementation, Cursor test and review, Codex
high-risk review. Tool and model are separate configuration. Switching tools
does not guarantee independent review. Configuration is snapshotted at start.

## Stage contracts

1. Plan: requirements/architecture, testable acceptance criteria; no edits.
2. Implement: bounded changes; applicable code-convention and code-review Mode A
   for Kotlin/Compose projects; quick checks; no commit.
3. Test: meaningful tests, relevant Maestro scenarios, targeted refactoring;
   next review includes all resulting source/test edits.
4. Review: requirements, conventions, code-review Mode B, correctness; read-only;
   APPROVE or REQUEST_CHANGES.
5. Verify: runner executes configured command arrays and records exit status,
   logs and checkout fingerprint. Required UI work needs executable UI checks.
   Missing devices/checks stop release.

Use `mw run TASK --once` for configured cross-tool execution. Manual work in the
current UI: `mw next TASK --tool manual`, perform one stage, write its JSON result,
then `mw record TASK --result PATH`. Disclose manual substitutions. Preserve
independent high-risk review. Never recursively launch from a stage prompt.

Failures stop. Diagnose before `mw repair`; retries are bounded and invalidate
old evidence. Explicit tool overrides are available; no silent automatic fallback.
External checkout edits invalidate readiness. Use one writer per checkout;
the runner locks concurrent workflow operations.

State is outside product roots under ~/.local/state/workflow. Keys stay in the
environment. Never add workflow/AI instructions to Android/MoSec roots. Never
post review comments without explicit authorization. The runner never commits
or pushes. Commit only if requested after gates pass; human what/why message,
no AI/tooling references. Existing standalone helpers and PR-review remain usable.
