# OpenCode Final Follow-Up Check (2026-07-02T13:53:27Z)

## What was done
- Centralized the generated OpenCode artifact list in `scripts/opencode/generate_opencode_port.py`.
- Updated the CI drift-check workflow to read generated artifact paths from the generator instead of duplicating them in YAML.
- Re-ran end-to-end verification of the OpenCode port and install flows.

## Key decisions
1. Keep the generated artifact list in the generator as the source of truth because it owns artifact creation.
2. Have CI query the generator with `--print-generated-files` so sync verification stays aligned with future artifact additions/removals.
3. Retain current skill-directory mismatch handling via install-time canonicalized symlink names; verification confirms this still works.

## Major changes
| File | Change |
|------|--------|
| `scripts/opencode/generate_opencode_port.py` | Added centralized generated artifact paths and a `--print-generated-files` CLI flag |
| `.github/workflows/opencode-sync-check.yml` | Reads generated artifact paths from the generator before `git diff` verification |

## Final verification
- `bash scripts/opencode/sync_upstream.sh` ✅
- `bash -n scripts/opencode/install_local_skills.sh scripts/opencode/sync_upstream.sh` ✅
- `python3 -m py_compile scripts/opencode/generate_opencode_port.py` ✅
- `python3 scripts/opencode/generate_opencode_port.py --print-generated-files` ✅
- Full install smoke test:
  - `bash scripts/opencode/install_local_skills.sh --profile main-standard --dest /tmp/opencode-final-main` ✅
  - Verified canonicalized symlinks exist for:
    - `cuequivariance`
    - `nvmolkit-usage`
- Minimal install smoke test:
  - `bash scripts/opencode/install_local_skills.sh --profile minimal-no-npx --dest /tmp/opencode-final-project` ✅
  - Verified installed skill set matches the expected six minimal-profile skills
- Drift check using generator-provided file list and `git diff --quiet` ✅

## Remaining suggested tasks
1. Validate the OpenCode port in a real OpenCode runtime session to confirm actual skill discovery behavior.
2. Plan a separate rename migration for `cuEquivariance` and `nvMolKit` source directories to eliminate legacy naming mismatches at the source.
3. Validate the upstream `skills` CLI OpenCode install path and upstream any required fix.
