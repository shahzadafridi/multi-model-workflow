# Validation

Validated on November 11, 2026:

- `python3 -m unittest discover -s tests -v`: 24 tests passed. Tests use real
  temporary Git repositories and deterministic fake provider executables; no
  paid model calls or product data are needed.
- Covered low/high routing; all five CLI adapters; manual handoffs; stale result
  rejection; source/index/untracked-file invalidation; required UI/check gates;
  failed verification; edits during verification/review; timeouts; bounded
  attempts/repairs; failed-plan recovery; estimated spend reservations; config
  snapshots; checkout locks; and shell metacharacter handling.
- Installer integration test verifies backups, idempotence, native command/skill
  formats, symlink launch, shell-block preservation and legacy flow compatibility.
- Python compilation and zsh syntax checks passed for changed runner/flow files.
- Local installation completed and a repeat installation updated zero files.
  `mw doctor` found Codex, Cursor, Claude Code, OpenCode, DeepSeek Harness and
  Maestro; a DeepSeek key is exported (its value was not printed).

Actual provider authentication/model entitlement and an end-to-end change on a
real product are not established by these tests. A live Cursor review attempt
returned no usable result and was stopped; no independent review approval is
claimed. No mobile/web product UI changed, so no Maestro device run was required
for this shell/Python workflow change. Product tasks still enforce configured
checks and their UI gate. At validation time this folder had no Git repository metadata;
repository publication was a separate subsequent step.

## Cost-focused update

The complete offline suite now passes 31 tests. Added coverage establishes:

- Routine non-UI medium-risk work completes with two CLI agent stages.
- Failed regular prechecks stop before any reviewer is launched.
- Missing required check configuration blocks CLI execution upfront.
- Passing prechecks do not grant readiness or replace fresh final verification.
- A second diagnosed repair uses the configured stronger implementation role.
- Separate test authoring remains configurable, and existing saved tasks retain
  their original stages and role configuration.
- Cost metrics keep estimates separate from user-reported usage; duplicate
  provider/reference pairs and nonfinite amounts are rejected.

Both updated skills pass the Skill Creator validator. Python compilation and
Git whitespace checks pass. These are workflow behavior tests with simulated
provider CLIs; they do not establish real-world dollar savings or defect rates.
