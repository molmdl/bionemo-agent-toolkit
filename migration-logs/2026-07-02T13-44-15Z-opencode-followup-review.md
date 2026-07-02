# OpenCode Follow-Up Review (2026-07-02T13:44:15Z)

## What was done
- Reviewed all follow-up items from `migration-logs/2026-07-02T13-29-26Z-opencode-port-fix.md` against the current OpenCode port implementation.
- Revalidated port generation and install scripts:
  - `bash scripts/opencode/sync_upstream.sh`
  - `bash -n scripts/opencode/install_local_skills.sh scripts/opencode/sync_upstream.sh`
- Updated OpenCode config guidance to avoid compatibility issues with legacy source directory names.
- Updated generator output format to remove non-standard JSON comment conventions.

## Deep review of follow-up items
1. **Rename source directories for mismatched names** — **Good to do (not urgent)**  
   - Status: real compatibility/readability issue for direct source-path discovery.
   - Impact if skipped: users pointing OpenCode directly at `plugins/.../skills` may miss two skills due to name validation.
   - Current mitigation: use `install_local_skills.sh`, which canonicalizes to SKILL frontmatter names.

2. **Wire `sync_upstream.sh` into CI** — **Good to do**  
   - Status: valid drift-prevention improvement.
   - Impact if skipped: OpenCode artifacts may silently drift from skill metadata.

3. **Add project-level `.opencode/skills/` structure** — **Good to do; now implemented via install flow**  
   - Status: valid and directly addresses compatibility for project-scoped installs.
   - Result: docs/config now standardize on `.opencode/skills` for config-based usage.

4. **Create TypeScript plugin for OpenCode tool-calling hooks** — **Optional / future enhancement**  
   - Status: not required for current SKILL.md-based port.
   - Risk if forced now: scope creep and maintenance burden without confirmed need.

5. **Test OpenCode skill discovery in real runtime** — **Good to do**  
   - Status: valid verification task.
   - Impact if skipped: compatibility assumptions remain unverified end-to-end.

6. **Validate `npx skills add ... --agent opencode` behavior** — **Good to do**  
   - Status: valid upstream interoperability check.
   - Impact if skipped: CLI-based install path may continue to target incorrect directories.

7. **Review `_comment` in `opencode.sample.json`** — **Real issue; fixed**  
   - Status: `_comment` is not schema-standard and can cause strict validation friction.
   - Result: removed `_comment` field from generated sample config.

## Key decisions
1. Keep source directory renames out of this change set (high churn, cross-repo references) and prefer canonicalized install destinations now.
2. Standardize project-scoped OpenCode config on `.opencode/skills` (populated via install script), not raw plugin source directories.
3. Keep OpenCode sample config schema-clean (no pseudo-comment keys).

## Major changes in this follow-up
| File | Change |
|------|--------|
| `scripts/opencode/generate_opencode_port.py` | Removed `_comment` from sample JSON output; changed sample `skills.paths` to `"<path-to-bionemo-agent-toolkit>/.opencode/skills"` |
| `opencode/config/opencode.sample.json` | Regenerated to match the new schema-clean sample path convention |
| `README.md` | Updated OpenCode install docs to include project-local install command and config path; documented mismatch-avoidance rationale |

## Suggested next tasks
1. Run OpenCode runtime verification in an actual session and confirm all expected skills are discoverable.
2. Add a CI check that runs `scripts/opencode/sync_upstream.sh` and fails on dirty git state.
3. Plan a dedicated rename migration for `cuEquivariance` and `nvMolKit` source directories (plus references) to remove legacy naming debt.
4. Validate upstream `skills` CLI behavior for `--agent opencode` and upstream a fix if path handling is still incorrect.
