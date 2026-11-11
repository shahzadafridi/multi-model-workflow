---
name: review-pr
description: >-
  Review a PR or branch with code-convention, code-review Mode B, and overall
  quality. Prefer slash /mw-review-pr (custom my-workflow prefix). Shell:
  review-pr. Brief: ~/workflow/prompts/pr-review.md.
---

# PR / branch review

Use **`/mw-review-pr`** in agent chats (or shell `review-pr`). Follow `~/workflow/prompts/pr-review.md`.

Passes: **code-convention** → **code-review** Mode B → overall quality / bad practices.
Output Blocking / Should fix / Nit → APPROVE | REQUEST CHANGES | COMMENT.

Bitbucket: draft findings → author YES → `review-pr-comment`. Menu: `/mw`.
