# Bitbucket setup (Orca + CLI)

For repositories hosted on **Bitbucket Cloud**, configure your own workspace and repository. There are **two separate logins** on the same machine:

| Auth | Used by | Purpose |
|---|---|---|
| **Orca** (`~/.orca/bitbucket-credential.*`) | Orca desktop app | Orca UI / worktree Bitbucket features |
| **`bkt` CLI** (OS keyring) | Terminals + agents (including **inside Orca**) | `bkt pr …`, `review-pr-comment`, scripted comments |

They do **not** share credentials. Log into both once per machine.

Agents running in **Orca terminals** use the same `bkt` install and keyring as any other terminal — once `bkt auth login … --web` succeeds, Orca agents can run `bb-status`, `bkt pr list`, and `review-pr-comment`.

## Check status anytime

```bash
bb-status
```

Or:

```bash
bkt auth status
bkt context list
```

## 1. Orca Bitbucket (app)

In **Orca**, sign in to Bitbucket via the app’s Bitbucket / account settings (creates `~/.orca/bitbucket-credential.json` + `.enc`).

This does **not** authenticate `bkt`. You still need step 2 for terminal PR comments.

## 2. `bkt` CLI (required for workflow comments)

Preferred (OAuth — browser, auto-refresh):

```bash
brew install bitbucket-cli   # provides `bkt`

bkt auth login https://bitbucket.org --kind cloud --web
```

Alternatives:

```bash
# Opens Atlassian API token page, then prompts locally
bkt auth login https://bitbucket.org --kind cloud --web-token

# Pipe a token (clipboard) — needs correct scopes; prefer --web
pbpaste | bkt auth login https://bitbucket.org --kind cloud \
  --username "you@company.com" --with-token
```

Verify:

```bash
bkt auth status
# expect: auth: oauth (or basic), user set, token source: keyring
```

### One-time context (workspace + default repo)

`bkt` needs an active context after login:

```bash
bkt context create work \
  --host "https://api.bitbucket.org/2.0" \
  --workspace your-workspace \
  --repo your-repository \
  --set-active

bkt pr list --limit 5
```

From a Bitbucket checkout (`origin` → `bitbucket.org:…`):

```bash
bkt pr list
bkt pr view 42
bkt pr diff 42
```

## 3. Review → author gate → comments (required)

Agents **must not** post Bitbucket comments until you approve — same rule in Cursor, Claude, and **Orca** agent tabs.

1. Run review: `review-pr 42` or `/mw-review-pr 42`
2. Agent writes findings to a draft file, e.g. `.workflow/pr-42-findings.md`
3. You read/edit the draft
4. Post only after typing **YES**:

```bash
# Default: --pending drafts (not visible until you submit in Bitbucket UI)
review-pr-comment 42 .workflow/pr-42-findings.md

# Visible immediately (still requires YES)
review-pr-comment 42 .workflow/pr-42-findings.md --publish
```

### Findings file format

```markdown
### general
Summary / overall verdict (REQUEST CHANGES / APPROVE).

### file:library/foo/src/Foo.kt:42
Inline comment body (Blocking/Should fix).

### file:library/foo/src/Bar.kt:10-15
Uses line 10 as the inline anchor.
```

## Why author review first

- Avoids noisy or wrong-line comments on Bitbucket
- `--pending` keeps drafts private until you submit the review in the UI
- Matches Android Studio MCP behavior (“pending until user submits”) when that auth works

## Android Studio Bitbucket MCP

May return **401** if the IDE plugin auth ≠ Orca / `bkt`. Fix in IDE Bitbucket settings separately. Workflow comments go through **`bkt`**, not the MCP.

## Agent rules (also in prompts)

When reviewing a Bitbucket PR (in Cursor, Claude, **or Orca**):

1. Produce findings locally first
2. **Ask the author** which comments to keep
3. Only then run `review-pr-comment` (or ask the author to run it)
4. Prefer `--pending` unless the author says publish

Never post comments autonomously.

If `bkt` is not logged in: tell the author to run `bb-status` and
`bkt auth login https://bitbucket.org --kind cloud --web`.
