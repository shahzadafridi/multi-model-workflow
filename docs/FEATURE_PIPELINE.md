# Feature pipeline

The canonical usage, routing, gate, budget and recovery reference is
[QUICKSTART.md](QUICKSTART.md). Defaults live in `config/default.json` and stage
contracts in `prompts/stages/`.

This version replaces interactive agent-launch sequences and unverified commit
prompts with a shared `mw` task runner. Existing /mw flow names remain available.
Terminal aliases now create saved tasks; use `mw run TASK` to execute them.

Review evidence and executable checks are bound to checkout contents. Failed or
missing required checks block readiness. All commits/pushes are explicit user
operations after verification. PR-only review and its author-approved external
comment path remain separate; see [BITBUCKET.md](BITBUCKET.md).
