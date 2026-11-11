# Compatibility entry point for legacy flow names. Sourced by the wrappers.
set -euo pipefail
flow="$1"
shift
runner="${0:A:h}/mw"
if (( $# == 0 )); then
  read -r 'brief?Task brief: '
  exec "$runner" start --flow "$flow" --brief "$brief"
fi
if [[ " $* " == *' --brief '* || "${1:-}" == (--help|-h) ]]; then
  exec "$runner" start --flow "$flow" "$@"
fi
pro=()
brief_parts=()
for arg in "$@"; do
  if [[ "$arg" == --pro ]]; then pro=(--pro); else brief_parts+=("$arg"); fi
done
exec "$runner" start --flow "$flow" "${pro[@]}" --brief "${(j: :)brief_parts}"
