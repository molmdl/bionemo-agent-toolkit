# OpenCode Skill Header Verification Summary (2026-07-03T10:18:43Z)

## What was done

- Logged versioned OpenCode format research in:
  - `migration-logs/2026-07-03T10-17-59Z-opencode-format-research.md`
- Verified all repository `SKILL.md` files against OpenCode-oriented checks:
  - frontmatter presence
  - required fields (`name`, `description`)
  - `name` regex compatibility
  - directory-name match checks
  - tool-related frontmatter key usage (`allowed-tools`)
- Checked hook compatibility applicability for OpenCode in this repo.
- Updated `README.md` with explicit OpenCode header-compatibility and hook notes.

## Verification results

- Total `SKILL.md` files scanned: **65**
- Files using `allowed-tools`: **40** (OpenCode-compatible because unknown frontmatter keys are ignored)
- Findings:
  1. Legacy intentional name-vs-directory mismatches (already handled by install-time canonicalization):
     - `library-skills/cuEquivariance/SKILL.md`
     - `library-skills/nvMolKit/SKILL.md`
     - `plugins/bionemo-agent-toolkit/skills/cuEquivariance/SKILL.md`
     - `plugins/bionemo-agent-toolkit/skills/nvMolKit/SKILL.md`
  2. Non-port workflow/vendor paths not part of OpenCode install/discovery flow:
     - `workflows/generative_protein_binder_design/SKILL.md` (no frontmatter index file)
     - `workflows/generative_protein_binder_design/complexa-binder-design/vendor/science-skills/alphafold_database_fetch_and_analyze/SKILL.md`
     - `workflows/generative_protein_binder_design/complexa-binder-design/vendor/science-skills/uniprot_database/SKILL.md`

## Hook compatibility status

- No OpenCode hook/plugin runtime config is currently shipped in this repo for execution-time tool hooks.
- Current OpenCode port is SKILL.md + install/config based, which remains compatible.

## Key decisions

1. Treat OpenCode-installable skill sets (`plugins/bionemo-agent-toolkit/skills` and their source skill directories) as migration-critical scope.
2. Keep `allowed-tools` unchanged for cross-agent reuse because OpenCode ignores unknown skill frontmatter keys.
3. Do not perform directory-rename migrations in this task; existing install scripts already canonicalize mismatched names.
4. Do not introduce OpenCode plugin hooks in this task; only compatibility verification was requested.

## Major changes

| File | Change |
|------|--------|
| `migration-logs/2026-07-03T10-17-59Z-opencode-format-research.md` | Added versioned OpenCode format research baseline (commit + file SHAs) |
| `README.md` | Added explicit OpenCode header-compatibility and hook applicability note |
| `migration-logs/2026-07-03T10-18-43Z-opencode-skill-header-verification.md` | Added completion summary, decisions, and verification findings |

## Suggested follow-up tasks

1. Optionally rename legacy source directories (`cuEquivariance`, `nvMolKit`) to canonical OpenCode-compatible names to remove install-time remapping.
2. Decide whether to keep or remove `allowed-tools` long term; if removed, preserve equivalent guidance in skill body text.
3. If workflow/vendor `SKILL.md` files should be OpenCode-discoverable later, normalize their directory naming and frontmatter for strict compatibility.
4. If OpenCode runtime hooks are needed, implement an explicit OpenCode plugin package/config and document it in `README.md`.
