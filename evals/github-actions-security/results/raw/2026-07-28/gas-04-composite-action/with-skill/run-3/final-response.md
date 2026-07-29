Everything looks correct. Summary of the checklist:

- [x] `actionlint` clean
- [x] `zizmor` clean (0 findings, exit 0), offline mode — no `GH_TOKEN` available so API-backed audits were skipped; noting this as reduced coverage
- [x] `permissions: {}` at workflow level, each job scoped to `contents: read`
- [x] `actions/setup-python` and `actions/cache` pinned to commit SHAs resolved from their latest releases (v7.0.0, v6.1.0) with version comments; `actions/checkout` already pinned
- [x] No `${{ }}` interpolation in a `run:` block — fixed the pre-existing echo step to use `env:`
- [x] `persist-credentials: false` on checkout, `timeout-minutes` on every job, `concurrency` added at workflow level
- [x] No self-hosted runners, no secrets, no `pull_request_target`

Structural-only change: didn't push to a branch to trigger a live workflow run, so this is verified via `actionlint`/`zizmor` and manual review, not an actual GitHub Actions execution.

**What changed:**
- `actions/setup-toolchain/action.yml`: pinned `setup-python`/`cache` to commit SHAs, added a "Lint with ruff" step after Python setup, and made the cache key `build-${{ inputs.version }}-${{ hashFiles('**/uv.lock') }}`.
- `.github/workflows/ci.yml`: added a `test-windows` job (same action + `python -m pytest`) on `windows-latest`, plus a `concurrency` block since the file was already being extended.
- `README.md`: updated the action's Purpose description to mention linting and the lockfile-aware cache key.
