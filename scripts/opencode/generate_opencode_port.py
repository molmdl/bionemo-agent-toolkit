#!/usr/bin/env python3
"""Generate opencode port assets from existing claude/codex plugin metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


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


def _read_minimal_skills(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _build_plugin(
    codex_plugin: dict, claude_plugin: dict, profile: str, skills: list[str]
) -> dict:
    plugin = dict(codex_plugin)
    plugin["targetAgent"] = "opencode"
    plugin["profile"] = profile
    plugin["requiresNpx"] = False
    plugin["skills"] = [f"./skills/{skill}" for skill in skills]
    plugin["displayName"] = claude_plugin.get(
        "displayName", codex_plugin.get("displayName", codex_plugin.get("name"))
    )
    if profile == "minimal-no-npx":
        interface = dict(plugin.get("interface", {}))
        interface["defaultPrompt"] = [
            "Predict the structure of insulin with Boltz2",
            "Dock a small molecule target with DiffDock",
            "Design a de novo binder for a target with RFdiffusion",
        ]
        plugin["interface"] = interface
    return plugin


def _build_marketplace(claude_marketplace: dict) -> dict:
    marketplace = dict(claude_marketplace)
    marketplace["name"] = "bionemo-agent-toolkit-opencode"
    marketplace["metadata"] = {
        "description": (
            "OpenCode marketplace for NVIDIA BioNeMo skills with standard and "
            "minimal (no npx) profiles."
        ),
        "version": claude_marketplace.get("metadata", {}).get("version", "0.1.0"),
    }
    marketplace["plugins"] = [
        {
            "name": "bionemo-agent-toolkit-opencode-standard",
            "source": "./plugins/bionemo-agent-toolkit/.opencode-plugin/plugin.json",
            "description": "Full standard OpenCode profile generated from upstream skills.",
        },
        {
            "name": "bionemo-agent-toolkit-opencode-minimal",
            "source": "./plugins/bionemo-agent-toolkit/.opencode-plugin/minimal-plugin.json",
            "description": "Minimal no-npx OpenCode profile with core skills/scripts only.",
        },
    ]
    return marketplace


def _build_workflow(profile: str, branch: str, skills: list[str]) -> dict:
    return {
        "name": f"opencode-{profile}",
        "branch": branch,
        "profile": profile,
        "requiresNpx": False,
        "skills": skills,
        "syncScript": "scripts/opencode/sync_upstream.sh",
        "installScript": "scripts/opencode/install_local_skills.sh",
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
    codex_plugin_path = plugin_root / ".codex-plugin" / "plugin.json"
    claude_plugin_path = plugin_root / ".claude-plugin" / "plugin.json"
    claude_marketplace_path = root / ".claude-plugin" / "marketplace.json"
    minimal_list_path = root / "scripts" / "opencode" / "minimal_skills.txt"

    all_skills = _list_skills(skills_dir)
    minimal_skills = _read_minimal_skills(minimal_list_path)
    unknown = sorted(set(minimal_skills) - set(all_skills))
    if unknown:
        raise ValueError(f"Unknown minimal skill(s): {', '.join(unknown)}")

    codex_plugin = _read_json(codex_plugin_path)
    claude_plugin = _read_json(claude_plugin_path)
    claude_marketplace = _read_json(claude_marketplace_path)

    standard_plugin = _build_plugin(
        codex_plugin=codex_plugin,
        claude_plugin=claude_plugin,
        profile="main-standard",
        skills=all_skills,
    )
    minimal_plugin = _build_plugin(
        codex_plugin=codex_plugin,
        claude_plugin=claude_plugin,
        profile="minimal-no-npx",
        skills=minimal_skills,
    )

    _write_json(plugin_root / ".opencode-plugin" / "plugin.json", standard_plugin)
    _write_json(plugin_root / ".opencode-plugin" / "minimal-plugin.json", minimal_plugin)
    _write_json(root / ".opencode" / "marketplace.json", _build_marketplace(claude_marketplace))
    _write_json(
        root / "opencode" / "workflows" / "main-standard.json",
        _build_workflow("main-standard", "main", all_skills),
    )
    _write_json(
        root / "opencode" / "workflows" / "minimal-no-npx.json",
        _build_workflow("minimal-no-npx", "minimal", minimal_skills),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
