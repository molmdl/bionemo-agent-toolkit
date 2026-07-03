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

## OpenCode permission / tool names (added 2026-07-03)

The prior research verified that `allowed-tools` is an unknown frontmatter field (OpenCode ignores it), but **did not check whether the tool-name values inside that field match OpenCode permission key names**.

OpenCode permission keys (from `permissions.mdx` and `tools.mdx`, ref `41a3cfcdd9...`):

| OpenCode permission key | Notes |
|-------------------------|-------|
| `bash`                  | shell execution |
| `read`                  | file reads |
| `edit`                  | all file modifications (`edit`, `write`, `apply_patch`) |
| `glob`                  | file globbing |
| `grep`                  | content search |
| `skill`                 | loading a skill |
| `task`                  | subagent launch |
| `question`              | asking user questions |
| `webfetch`              | URL fetch |
| `websearch`             | web search |
| `lsp`                   | LSP queries (experimental) |
| `todowrite`             | todo list management |
| `external_directory`    | paths outside working dir |
| `doom_loop`             | repeated identical tool calls |
| `mcp_<name>_*`          | MCP server tools (wildcard) |

Tool names used in this repo's `allowed-tools` values: `Bash`, `Read`, `Write`, `AskUserQuestion`.

Mapping to OpenCode permission keys:
- `Bash` → `bash` (different casing; functionally analogous)
- `Read` → `read` (different casing; functionally analogous)
- `Write` → `edit` (different name; OpenCode `edit` permission covers `write` and `apply_patch`)
- `AskUserQuestion` → `question` (different name)

**Impact:** Because OpenCode ignores the `allowed-tools` frontmatter field entirely, the mismatched names cause no runtime error today. However, they are **not valid OpenCode permission keys** and cannot be used in `opencode.json` `permission` blocks or agent frontmatter permission overrides as-is. Adding OpenCode-native permission/tool enforcement in a future task requires mapping these names to their correct OpenCode equivalents.

**Future plan:** Add OpenCode-format `permission` and `tools` configuration support to skills and the sample `opencode.json` config, using the OpenCode key names above.

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
