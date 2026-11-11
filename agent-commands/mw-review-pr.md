---
description: "Review a PR or branch with code-convention, code-review Mode B, and overall quality. Shell: review-pr. Brief: ~/workflow/prompts/pr-review.md."
argument-hint: "[pr-number|branch|url]"
disable-model-invocation: true
---

# /mw-review-pr

Custom PR / branch review from `~/workflow`. Arguments: `$ARGUMENTS`

## Scope

- If `$ARGUMENTS` has a PR number or URL: use `gh pr view` / `gh pr diff` (and checks).
- Else review current branch vs `origin/main` or `origin/master` (or the base the user names).
- Read surrounding context in changed files; do not judge the hunk alone.

## Required passes

1. **code-convention** skill — all changed Kotlin/Compose/KMP/Android (related) files
2. **code-review** skill — Mode B checklist (Blocking / Should fix / Nit)
3. **Overall quality** — bugs, security/PII, dead code, layering leaks, missing edge cases, performance, fragile contracts, missing tests/Maestro for UI, naming/duplication, breaking changes

Also follow `~/workflow/prompts/pr-review.md` if present.

## Output

For each finding:
`<file>:<line> — <Blocking|Should fix|Nit> — <title> — <why> — <fix>`

End with counts, `APPROVE` / `REQUEST CHANGES` / `COMMENT`, and top must-fixes.

## Bitbucket comments — author gate (mandatory)

Never post Bitbucket comments on your own.

1. Write a findings draft (`.workflow/pr-<id>-findings.md`) with `### general` / `### file:path:line` blocks.
2. Ask the **author** to review/edit the draft.
3. Only after they confirm, run (or ask them to run):

```bash
review-pr-comment <pr-id> .workflow/pr-<id>-findings.md
# pending drafts by default; --publish only if author asks
```

If `bkt` is not authenticated: tell them `bb-status` and
`bkt auth login https://bitbucket.org --kind cloud --web`.
Details: `~/workflow/docs/BITBUCKET.md`.

Do not commit/push unless the author explicitly asks after the review.
Never write AGENTS.md or AI workflow files into Android/MoSec project roots.
Menu: `/mw`. Shell: `review-pr`.
