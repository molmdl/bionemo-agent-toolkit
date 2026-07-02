# OpenCode Port Fix (2026-07-02T13:29:26Z)

## Problem Statement

The previous OpenCode port (logged in `2026-07-01T18-21-48Z-opencode-port.md`)
incorrectly copied the Claude Code / Codex marketplace and plugin JSON formats to
OpenCode.  These formats do not exist in OpenCode and had no effect on the agent.

## Research Findings

OpenCode (https://opencode.ai, `anomalyco/opencode` on GitHub) has its own
skill/plugin system that is **entirely different** from Claude Code or Codex:

### OpenCode Skill Discovery Paths

Skills are `SKILL.md` files with YAML frontmatter.  OpenCode discovers them from:

| Scope   | Path                                              |
|---------|---------------------------------------------------|
| Project | `.opencode/skills/<name>/SKILL.md`               |
| Project | `.agents/skills/<name>/SKILL.md`                 |
| Project | `.claude/skills/<name>/SKILL.md` (compat)        |
| Global  | `~/.config/opencode/skills/<name>/SKILL.md`      |
| Global  | `~/.agents/skills/<name>/SKILL.md`               |
| Global  | `~/.claude/skills/<name>/SKILL.md` (compat)      |
| Config  | `skills.paths` array in `opencode.json`          |

The global config directory follows XDG Base Directory Specification:
`$XDG_CONFIG_HOME/opencode` (defaults to `~/.config/opencode`).

### OpenCode Skill Name Requirements

OpenCode validates that:
- `name:` in SKILL.md frontmatter matches the directory name containing it
- Name format: `^[a-z0-9]+(-[a-z0-9]+)*$` (lowercase, hyphens only)
- Length: 1–64 characters

### OpenCode Plugin System (TypeScript/JS)

OpenCode plugins are TypeScript/JavaScript files, not JSON manifests.  They are
declared in `opencode.json` via the `plugin` array (package names or file paths),
and they export a `Plugin` function returning `Hooks` (including `tool` definitions).
The `.opencode-plugin/plugin.json` format from the prior port is not recognized.

### What Does NOT Exist in OpenCode

- `.opencode-plugin/` directory convention
- `targetAgent`, `requiresNpx`, `profile`, `displayName` fields in plugin JSON
- Marketplace concept (no equivalent of `.claude-plugin/marketplace.json`)
- `~/.opencode/skills/` as a valid global skills directory

## Key Decisions

1. **Install destination**: Changed from `~/.opencode/skills/` (non-existent) to
   `~/.config/opencode/skills/` (XDG-compliant, what OpenCode actually reads).

2. **Skill directory naming**: The install script now reads the `name:` field from
   each `SKILL.md` frontmatter and uses that as the target symlink directory name.
   This is required because OpenCode validates that directory name == `name:` field.
   Two skills have mismatched names in the repo that are auto-corrected on install:
   - `cuEquivariance/` → installs as `cuequivariance/` (matches `name: cuequivariance`)
   - `nvMolKit/` → installs as `nvmolkit-usage/` (matches `name: nvmolkit-usage`)

3. **Generator script**: `generate_opencode_port.py` no longer reads Claude/Codex
   plugin JSON as its source of truth.  It now reads skill metadata directly and
   produces the correct OpenCode artifacts (`opencode.sample.json`).

4. **Correct install mechanism**: Two supported approaches documented:
   - **Global symlink**: `install_local_skills.sh` symlinks each skill dir under
     `~/.config/opencode/skills/<name>/`
   - **Config-based**: User adds `skills.paths` to their `opencode.json`

5. **Removed wrong fields from workflow JSON**: Removed `requiresNpx`, `syncScript`,
   and other non-OpenCode fields from `opencode/workflows/*.json`.

6. **`.opencode-plugin/plugin.json`**: Repurposed as a human-readable reference
   document with a `_note` field clarifying it is not an OpenCode plugin manifest.

7. **`.opencode/marketplace.json`**: Replaced with a reference document clarifying
   OpenCode has no marketplace concept; real install instructions are provided.

## Major Changes

| File | Change |
|------|--------|
| `scripts/opencode/install_local_skills.sh` | Fixed dest to `~/.config/opencode/skills/`; reads `name:` from SKILL.md for target dir |
| `scripts/opencode/generate_opencode_port.py` | Rewritten: no longer copies Claude/Codex format; generates `opencode.sample.json` |
| `scripts/opencode/sync_upstream.sh` | Updated comment |
| `opencode/config/opencode.sample.json` | New — correct `skills.paths` config snippet for users |
| `opencode/workflows/main-standard.json` | Regenerated; removed wrong OpenCode fields |
| `opencode/workflows/minimal-no-npx.json` | Regenerated; removed wrong OpenCode fields |
| `plugins/bionemo-agent-toolkit/.opencode-plugin/plugin.json` | Replaced with reference doc (not an OpenCode format) |
| `plugins/bionemo-agent-toolkit/.opencode-plugin/minimal-plugin.json` | Replaced with reference doc |
| `.opencode/marketplace.json` | Replaced with reference doc (OpenCode has no marketplace) |
| `README.md` | Updated OpenCode section with correct install instructions |

## Suggested Follow-Up Tasks

1. **Rename source directories** for skills with mismatched names to avoid confusion:
   - Rename `library-skills/cuEquivariance/` → `library-skills/cuequivariance/`
   - Rename `library-skills/nvMolKit/` → `library-skills/nvmolkit-usage/`
   - Also rename in `plugins/bionemo-agent-toolkit/skills/`
   - Update README skill catalog table and all cross-references
   - This eliminates the warning in `generate_opencode_port.py` and `install_local_skills.sh`

2. **Wire `sync_upstream.sh` into CI** to auto-check OpenCode artifacts stay in sync
   with skill changes (validate workflow JSONs match actual skill directories).

3. **Project-level `.opencode/skills/` structure**: Consider adding a project-level
   `.opencode/skills/` directory that symlinks to the plugin skills for users who
   clone this repo and open it in OpenCode directly.

4. **TypeScript plugin for tool-calling**: If BioNeMo skills need to expose actual
   OpenCode tool-call hooks (beyond SKILL.md instructions), create a TypeScript
   plugin using the `@opencode-ai/plugin` SDK.  Skills are context/instructions;
   tools are executable functions callable by the agent.

5. **Test OpenCode skill discovery**: Validate skill loading end-to-end in a real
   OpenCode session (e.g., confirm that `boltz2-nim` appears in `<available_skills>`).

6. **Validate `npx skills add ... --agent opencode`**: Check if the upstream `skills`
   CLI correctly installs for OpenCode.  If it still uses the wrong path, file an
   upstream issue or add a post-install hook to redirect to the correct location.

7. **Review `_comment` field in `opencode.sample.json`**: JSON does not support
   comments natively.  The `_comment` key is a convention but `$schema` validation
   may flag it.  Consider moving the note to a companion README instead.
