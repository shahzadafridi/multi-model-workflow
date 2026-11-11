# Shared helpers for feature-pipeline flow commands.
# Location: ~/workflow/bin — sourced by flow scripts.

: "${WORKFLOW_HOME:=${0:A:h:h}}"

fp_banner() {
  print -P "%F{cyan}═══ $1 %F{default}"
  print -P "%F{white}$2%f"
  print ""
}

fp_pause() {
  print -P "%F{yellow}›%f $1"
  print -n "Press Enter when ready (Ctrl-C to abort)… "
  read -r _
}

fp_pr_review_prompt() {
  local prompt_file="${WORKFLOW_HOME}/prompts/pr-review.md"
  local extra="${1:-}"
  print "=== PR REVIEW ==="
  if [[ -n "$extra" ]]; then
    print "Target: ${extra}"
  else
    print "Target: current branch vs origin/main (or named base)"
  fi
  print ""
  if [[ -f "$prompt_file" ]]; then
    cat "$prompt_file"
  else
    print "Apply code-convention + code-review (Mode B) + overall bad-practice pass."
    print "Output Blocking / Should fix / Nit → APPROVE | REQUEST CHANGES | COMMENT."
  fi
  if [[ -n "$extra" ]]; then
    print ""
    print "Author target / notes: ${extra}"
  fi
}

fp_run_pr_review() {
  local target="${1:-}"
  fp_pause "Stage: PR REVIEW — code-convention + code-review + overall quality (Cursor Opus)"
  print "Paste the brief below into the agent (already printed). Prefer reviewing with gh pr diff when a PR # is given."
  print ""
  fp_pr_review_prompt "$target"
  print ""
  print "Starting opus-review…"
  opus-review
}
