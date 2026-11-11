# Design and migration decisions

The previous flow spawned interactive agents with copy/paste tips. Closing one
agent advanced to the next without validating its result. The Maestro helper
ignored process failure, and the commit helper could stage the whole checkout.
Slash prompts could execute a separate in-chat interpretation of those rules.
Those paths did not share a durable task specification or review/test evidence.

The migration retains named flows, standalone stage helpers, PR-only review,
convention/review skills and Maestro compatibility. A small standard-library
runner now owns task creation, stage transitions, budgets, invalidation and
verification. Native UI commands are adapters to that runner. No daemon, service,
database, model SDK, automatic worktree, or new secret store is necessary.

State uses atomic JSON replacement and a nonblocking per-checkout process lock.
Each task captures its config, brief, chosen risk/UI requirement, criteria, stage
index, attempts, repairs, estimates, active execution time and event history.
Each stage gets a prompt, structured result and (for CLI execution) output log.
Review and checks are bound to HEAD, Git index and working files. Model results
are advisory evidence; executable checks record actual process status separately.
Ignored/external files and live services are deliberately outside the fingerprint.

Routing is impact-aware but caller-selected: high risk reserves stronger roles;
routine non-UI tasks skip premium planning and separate test authoring. Default model
identifiers preserve existing DeepSeek configuration; Codex inherits its configured
model. Cursor Auto does not imply a fixed underlying model, price or independence.
Replace role mappings after measuring outcomes in your actual accounts.

Structured result contract:

```json
{
  "stage": "review",
  "fingerprint": "input fingerprint copied from the stage prompt",
  "verdict": "APPROVE",
  "summary": "Evidence, affected files, unresolved risks and actual tool/model",
  "acceptance_criteria": ["Concrete testable behavior"],
  "findings": []
}
```

Plan/implement/test use PASS or FAIL; review uses APPROVE or REQUEST_CHANGES.
Plan and unplanned implementation must supply criteria. Invalid/stale/missing
results cannot advance the stage. Failed verdicts require diagnosed, bounded
repair. CLI failures retain a pending attempt for inspection/recording or repair;
there is no blind retry or implicit fallback. CLI permissions remain in effect.

Only configured argument-array checks can release final readiness. A missing
required UI command blocks it. Later source edits invalidate approval. Test
authoring occurs before review so test/refactor edits are covered. Checks that
generate source changes force review again. The runner does not commit; this
avoids unintentionally staging unrelated user work. Native UI flows can complete
a requested commit after checking readiness and deliberately selecting files.

Limitations: trusted local agents can still edit state; this is not an adversarial
policy engine. Risk classification and test relevance need engineering judgment.
Manual chat time, provider billing and external editor concurrency are not fully
observable. File fingerprints can be costly for very large nonignored trees;
ignore build outputs appropriately. API quota errors and tool trust prompts stop
for inspection rather than triggering speculative model substitutions.

## Pilot before optimizing further

Use comparable small fixes, normal features, complex cross-module changes and
regression-sensitive work. Compare this workflow with the previous sequence and
a single-agent baseline. Save task history and provider usage for each run.
Measure accepted-change cost (including repairs and human time), end-to-end time,
first-pass acceptance, attempts/repairs, intervention time and later defects.
Keep the same acceptance criteria/checks for fair comparisons. Repeat across
several tasks; revise routing based on observed quality and total cost rather
than a single model leaderboard or nominal token price. Historical artifacts
support this experiment; no automatic savings estimate is asserted.

## Cost-focused routing update

New non-UI medium-risk tasks use implement → precheck → review → verify. The
implementer owns regression tests; a separate test-authoring agent remains for
high-risk and UI tasks. Regular checks run before paid review. Required check
configuration is validated before any CLI launch, avoiding spend on tasks that
cannot pass their release gate. Final verification runs fresh after review;
prechecks never substitute for approval or final checks.

After two diagnosed repairs, implementation selects the configured stronger role
without downgrading risk or UI requirements. Limits still stop further loops.
Existing tasks keep their captured configuration/stages.

Cost entries accept non-overlapping, user-reported dashboard amounts with a unique
provider/reference. Metrics expose stage launches, repairs, execution time, failed
prechecks, estimates and reported USD without pretending to retrieve billing.
The reduction from three to two routine agent stages is structural; actual dollar
savings and defect rates must be established on comparable verified fixes.
