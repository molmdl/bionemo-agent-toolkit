# OpenCode Format Research (2026-07-03T10:17:59Z)

## Research basis (versioned)

- OpenCode upstream repository: `anomalyco/opencode`
- Repository default ref observed via API responses: commit `41a3cfcdd9010693e2ec8daea777d007c07ba5bb`
- Skills spec source file:
  - `packages/web/src/content/docs/skills.mdx`
  - blob SHA: `2ce88ea5682f54abba56f1f56e1ea67e3eb851b4`
- Runtime loader source file:
  - `packages/core/src/skill.ts`
  - blob SHA: `be1cd1d49adcc18643ca3e799d1b00af5313b786`

## Current OpenCode SKILL.md compatibility rules (from upstream docs/code)

1. Skill discovery paths include:
   - `.opencode/skills/<name>/SKILL.md`
   - `~/.config/opencode/skills/<name>/SKILL.md`
   - `.agents/skills/<name>/SKILL.md` and `.claude/skills/<name>/SKILL.md` compatibility paths
2. Required frontmatter fields:
   - `name`
   - `description`
3. Documented optional fields:
   - `license`
   - `compatibility`
   - `metadata` (string-to-string map in docs)
4. Name constraints:
   - 1–64 chars
   - regex `^[a-z0-9]+(-[a-z0-9]+)*$`
   - should match containing directory name
5. Unknown frontmatter fields are ignored by OpenCode.

## Hooks compatibility findings

- No OpenCode SKILL.md hook frontmatter field is documented in the skills spec.
- OpenCode extensibility hooks are implemented through OpenCode plugin/config mechanisms, not SKILL.md headers.
- Therefore, SKILL.md compatibility verification should focus on skill frontmatter fields and naming; hook validation only applies if the repo defines OpenCode hook/plugin config.

## Scope adopted for verification

- Verify all repository `SKILL.md` files for:
  - frontmatter presence
  - required fields
  - name regex and directory-name compatibility where the file is intended as an installable/discoverable skill
  - usage of non-standard fields (notably tool-related `allowed-tools`) and whether they remain OpenCode-compatible (ignored vs required)
- Verify whether this repository currently defines OpenCode hook/plugin config that needs migration.
