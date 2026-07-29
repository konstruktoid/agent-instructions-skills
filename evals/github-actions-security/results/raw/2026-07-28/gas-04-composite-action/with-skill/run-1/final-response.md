All changes are complete and verified. Summary:

**`actions/setup-toolchain/action.yml`**
- Added a `Lint with ruff` step after the toolchain/version-report steps (installs and runs `ruff check .`)
- Cache key is now `build-${{ inputs.version }}-${{ hashFiles('**/uv.lock') }}` so a lockfile change invalidates the cache
- Pinned `actions/setup-python` and `actions/cache` to their latest release commit SHAs (v7.0.0, v6.1.0), matching the repo's existing SHA-pinning convention for `actions/checkout`
- Fixed a pre-existing template-injection issue zizmor flagged: `${{ inputs.version }}` is now passed via `env:` rather than interpolated directly into the `run:` shell string

**`.github/workflows/ci.yml`**
- Added a `test-windows` job (`windows-latest`) running the same checkout → `setup-toolchain` → pytest steps as `test`, so both platforms are covered
- Added a workflow-level `concurrency` block (zizmor flagged its absence)

**`README.md`** — updated the actions table and added a CI matrix table listing both jobs/runners.

Verification: `actionlint` and `zizmor --persona=pedantic .` both ran clean (exit 0) after one fix cycle. I could not actually execute the workflow on GitHub Actions — there's no configured remote and no `gh` auth in this environment — so this is verified structurally (lint + security audit) but not via a live run.
