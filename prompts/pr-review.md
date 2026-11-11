# PR / branch review brief

Perform a full review. Do **not** commit or push unless the author explicitly asks after the review.

## Scope

1. If a PR number/URL was given, use `gh pr view` / `gh pr diff` (and checks if available).
2. Otherwise review `git diff` against the default base (`origin/main` or `origin/master`, or the branch the author names).
3. Read enough surrounding context in changed files — do not review the diff alone in isolation.

## Required skill passes

### A. code-convention
Apply the **code-convention** skill to all changed Kotlin / Compose / KMP / Android (and related) files. Flag every applicable violation.

### B. code-review
Apply the **code-review** skill in **Mode B** (the installed review checklist). Walk Blocking / Should fix / Nit.

### C. Overall quality / bad practices
Also look for (even if not listed in the skills):

- Bugs, logic errors, race conditions, incorrect null/error handling
- Security / PII / secrets / unsafe logging
- Dead code, unused imports on touched files, commented-out leftovers
- Leaky architecture (wrong layer, domain depending on transport, UI doing business logic)
- Missing edge cases, empty/error/loading states
- Performance (unnecessary recomposition, main-thread I/O, N+1, unbounded collections)
- API / contract mismatches, fragile stringly-typed checks
- Tests missing for risky changes; Maestro gaps if UI flow changed
- Unclear naming, god functions/classes, duplication
- Breaking changes without migration/notes

## Output format

For each finding:
`<file>:<line> — <Blocking|Should fix|Nit> — <short title> — <why> — <suggested fix>`

End with:

1. Counts per severity
2. Overall: `APPROVE` / `REQUEST CHANGES` / `COMMENT`
3. Top 3 must-fix items (if any)
4. Optional: short summary of what the PR does well

Do not rewrite the whole PR unless asked. Prefer precise, actionable comments.

## Bitbucket comments (author gate — mandatory)

Do **not** post comments to Bitbucket automatically.

1. Write findings to a draft file (e.g. `.workflow/pr-<id>-findings.md`) using:

```markdown
### general
…

### file:path/to/File.kt:42
…
```

2. Show the draft to the **author** and ask which items to keep / edit.
3. Only after the author confirms, they (or you with their explicit YES) run:

```bash
review-pr-comment <pr-id> .workflow/pr-<id>-findings.md
# default = pending drafts; add --publish only if author asks
```

If `bkt` is not logged in, tell the author to run `bb-status` and `bkt auth login https://bitbucket.org --kind cloud --web`.
See `~/workflow/docs/BITBUCKET.md`.
