#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

python3 "${SCRIPT_DIR}/generate_opencode_port.py" --repo-root "${REPO_ROOT}"
echo "OpenCode port artifacts regenerated from upstream claude/codex plugin metadata."
