#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROFILE="${PROFILE:-main-standard}"
# OpenCode global skill directory follows XDG: ~/.config/opencode/skills/
# See: https://opencode.ai/docs/skills
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
DEST="${DEST:-${XDG_CONFIG_HOME}/opencode/skills}"

usage() {
  cat <<'EOF'
Usage: install_local_skills.sh [--profile main-standard|minimal-no-npx] [--dest PATH]

Installs BioNeMo SKILL.md files for OpenCode by symlinking each skill directory
into the OpenCode global skills folder (~/.config/opencode/skills/ by default).

OpenCode discovers skills from:
  - ~/.config/opencode/skills/<name>/SKILL.md  (global, this script's default)
  - .opencode/skills/<name>/SKILL.md            (project-local)
  - .agents/skills/<name>/SKILL.md              (agent-compatible)
  - skills.paths in opencode.json               (config-based)

Each skill subdirectory name MUST match the 'name:' field in its SKILL.md
frontmatter.  This script reads the frontmatter name and uses it as the
target directory name, correcting any case mismatches from the source repo.

Options:
  --profile main-standard|minimal-no-npx   Skill profile to install (default: main-standard)
  --dest PATH                              Override install directory
  -h, --help                               Show this help

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
import pathlib
import re
import shutil
import sys


def _read_skill_name(skill_md: pathlib.Path) -> str:
    """Parse the 'name:' field from SKILL.md YAML frontmatter."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"No frontmatter in {skill_md}")
    end = text.find("---", 3)
    if end == -1:
        raise ValueError(f"Frontmatter in {skill_md} is missing closing '---' delimiter")
    frontmatter = text[3:end]
    for line in frontmatter.splitlines():
        m = re.match(r"^name:\s*(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    raise ValueError(f"No 'name:' field found in frontmatter of {skill_md}")


workflow_path = pathlib.Path(sys.argv[1])
repo_root = pathlib.Path(sys.argv[2])
dest_root = pathlib.Path(sys.argv[3]).expanduser().resolve()

workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
skills = workflow.get("skills", [])
skills_root = repo_root / "plugins" / "bionemo-agent-toolkit" / "skills"

for skill_dir_name in skills:
    source = skills_root / skill_dir_name
    if not source.is_dir():
        raise SystemExit(f"Missing skill source: {source}")

    skill_md = source / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit(f"Missing SKILL.md in: {source}")

    # Use the 'name:' from frontmatter as the target directory name.
    # OpenCode requires the directory name to match the 'name:' field exactly.
    skill_name = _read_skill_name(skill_md)
    target = dest_root / skill_name

    if target.exists() or target.is_symlink():
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
    target.symlink_to(source.resolve())
    print(f"linked {target} -> {source.resolve()}")
PY

echo ""
echo "Installed ${PROFILE} skills to ${DEST}."
echo ""
echo "OpenCode will discover skills automatically from this directory."
echo "You can also add a skills.paths entry to your opencode.json:"
echo ""
DEST_RESOLVED="$(python3 -c "import pathlib, sys; print(pathlib.Path(sys.argv[1]).expanduser().resolve())" "${DEST}")"
echo "  {\"skills\": {\"paths\": [\"${DEST_RESOLVED}\"]}}"
echo ""
