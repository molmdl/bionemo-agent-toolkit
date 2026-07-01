#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROFILE="${PROFILE:-main-standard}"
DEST="${DEST:-$HOME/.opencode/skills}"

usage() {
  cat <<'EOF'
Usage: install_local_skills.sh [--profile main-standard|minimal-no-npx] [--dest PATH]

Installs BioNeMo skills for OpenCode without npx by symlinking local skill folders.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      PROFILE="$2"
      shift 2
      ;;
    --dest)
      DEST="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

case "${PROFILE}" in
  main-standard|minimal-no-npx) ;;
  *)
    echo "Invalid profile: ${PROFILE}" >&2
    exit 1
    ;;
esac

WORKFLOW_JSON="${REPO_ROOT}/opencode/workflows/${PROFILE}.json"
if [[ ! -f "${WORKFLOW_JSON}" ]]; then
  echo "Missing workflow profile file: ${WORKFLOW_JSON}" >&2
  echo "Run scripts/opencode/sync_upstream.sh first." >&2
  exit 1
fi

mkdir -p "${DEST}"

python3 - <<'PY' "${WORKFLOW_JSON}" "${REPO_ROOT}" "${DEST}"
from __future__ import annotations
import json
import os
import pathlib
import shutil
import sys

workflow_path = pathlib.Path(sys.argv[1])
repo_root = pathlib.Path(sys.argv[2])
dest_root = pathlib.Path(sys.argv[3]).expanduser().resolve()

workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
skills = workflow.get("skills", [])
skills_root = repo_root / "plugins" / "bionemo-agent-toolkit" / "skills"

for skill in skills:
    source = skills_root / skill
    if not source.is_dir():
        raise SystemExit(f"Missing skill source: {source}")
    target = dest_root / skill
    if target.exists() or target.is_symlink():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    target.symlink_to(source)
    print(f"linked {target} -> {source}")
PY

echo "Installed ${PROFILE} skills to ${DEST} (no npx required)."
