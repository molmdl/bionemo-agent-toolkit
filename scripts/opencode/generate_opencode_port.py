#!/usr/bin/env python3
"""Generate opencode port assets from existing skill metadata.

Unlike the Claude/Codex port (which uses a plugin.json marketplace format),
OpenCode discovers skills via SKILL.md files in specific directories and via
the 'skills.paths' field in opencode.json.  This script generates:

  opencode/config/opencode.sample.json   - ready-to-use opencode.json snippet
  opencode/workflows/main-standard.json  - workflow metadata (skill list)
  opencode/workflows/minimal-no-npx.json - minimal workflow metadata

It no longer generates a .opencode-plugin/plugin.json in the Claude/Codex
marketplace format because that format is not recognized by OpenCode.

OpenCode skill installation:
  Global  : ~/.config/opencode/skills/<name>/SKILL.md
  Project : .opencode/skills/<name>/SKILL.md
  Config  : skills.paths in opencode.json (any directory with */SKILL.md)

See: https://opencode.ai/docs/skills
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def _list_skills(skills_dir: Path) -> list[str]:
    return sorted(
        p.name
        for p in skills_dir.iterdir()
        if p.is_dir() and (p / "SKILL.md").exists()
    )


def _read_skill_name(skill_dir: Path) -> str:
    """Parse the 'name:' field from SKILL.md YAML frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"No frontmatter in {skill_md}")
    end = text.find("---", 3)
    if end == -1:
        raise ValueError(f"Frontmatter in {skill_md} is missing closing '---' delimiter")
    for line in text[3:end].splitlines():
        m = re.match(r"^name:\s*(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    raise ValueError(f"No 'name:' field found in frontmatter of {skill_md}")


def _read_minimal_skills(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _build_opencode_sample(skills_dir: Path) -> dict:
    """Build a ready-to-use opencode.json snippet.

    Users can paste this into their project's opencode.json or into
    ~/.config/opencode/opencode.json for global availability.

    The path placeholder must be replaced with the actual absolute path to the
    cloned bionemo-agent-toolkit repository on the user's machine.
    """
    return {
        "$schema": "https://opencode.ai/config.json",
        "skills": {
            "paths": [
                "<path-to-bionemo-agent-toolkit>/.opencode/skills"
            ]
        }
    }


def _build_workflow(profile: str, branch: str, skills: list[str]) -> dict:
    return {
        "name": f"opencode-{profile}",
        "branch": branch,
        "profile": profile,
        "skills": skills,
        "installScript": "scripts/opencode/install_local_skills.sh",
        "configDocs": "opencode/config/opencode.sample.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Repository root.",
    )
    args = parser.parse_args()

    root = args.repo_root.resolve()
    plugin_root = root / "plugins" / "bionemo-agent-toolkit"
    skills_dir = plugin_root / "skills"
    minimal_list_path = root / "scripts" / "opencode" / "minimal_skills.txt"

    all_skill_dirs = _list_skills(skills_dir)
    minimal_skills = _read_minimal_skills(minimal_list_path)
    unknown = sorted(set(minimal_skills) - set(all_skill_dirs))
    if unknown:
        raise ValueError(f"Unknown minimal skill(s) in minimal_skills.txt: {', '.join(unknown)}")

    # Validate that each skill's SKILL.md name matches OpenCode's requirements
    # (lowercase alphanumeric + hyphens only; must match directory name)
    opencode_name_re = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    name_issues: list[str] = []
    for skill_dir_name in all_skill_dirs:
        try:
            skill_name = _read_skill_name(skills_dir / skill_dir_name)
        except ValueError as e:
            name_issues.append(str(e))
            continue
        if not opencode_name_re.match(skill_name):
            name_issues.append(
                f"{skill_dir_name}: SKILL.md name '{skill_name}' does not match "
                f"OpenCode name pattern (^[a-z0-9]+(-[a-z0-9]+)*$)"
            )
        if skill_name != skill_dir_name:
            # This is a warning, not an error — the install script handles the rename.
            print(
                f"[warn] {skill_dir_name}: SKILL.md name '{skill_name}' differs from "
                f"directory name. install_local_skills.sh will symlink as '{skill_name}'."
            )
    if name_issues:
        for issue in name_issues:
            print(f"[error] {issue}")
        raise SystemExit("Fix skill name issues before generating OpenCode port.")

    # Generate sample opencode.json config (the correct install mechanism)
    sample_config = _build_opencode_sample(skills_dir)
    _write_json(root / "opencode" / "config" / "opencode.sample.json", sample_config)

    # Generate workflow metadata
    _write_json(
        root / "opencode" / "workflows" / "main-standard.json",
        _build_workflow("main-standard", "main", all_skill_dirs),
    )
    _write_json(
        root / "opencode" / "workflows" / "minimal-no-npx.json",
        _build_workflow("minimal-no-npx", "minimal", minimal_skills),
    )

    print("OpenCode port artifacts generated:")
    print(f"  opencode/config/opencode.sample.json  — paste into opencode.json to add all skills")
    print(f"  opencode/workflows/main-standard.json — full skill list metadata")
    print(f"  opencode/workflows/minimal-no-npx.json — minimal skill list metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
