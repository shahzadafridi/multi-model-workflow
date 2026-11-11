#!/bin/zsh
# Install user-level integrations only; no product checkout files or secrets.
set -euo pipefail
exec python3 "${0:A:h}/lib/install_workflow.py" "$@"
