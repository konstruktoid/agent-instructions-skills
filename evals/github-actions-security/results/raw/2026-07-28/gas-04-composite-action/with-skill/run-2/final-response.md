All changes are complete and verified:

**`actions/setup-toolchain/action.yml`**
- Pinned `actions/setup-python` and `actions/cache` to resolved commit SHAs (latest releases v7.0.0 / v6.1.0), matching the existing repo convention.
- Cache key now includes `hashFiles('**/uv.lock')`, so a lockfile change invalidates the cache.
- Added a ruff lint step (`astral-sh/ruff-action`, pinned to v4.1.0) after the toolchain install.
- Fixed a pre-existing template-injection issue zizmor flagged on the `echo` step by routing the input through `env:` instead of interpolating it directly into `run:`.

**`.github/workflows/ci.yml`**
- Added a `test-windows` job that runs the same composite action and `pytest` suite on `windows-latest`.
- Added a `concurrency` block (zizmor flagged the missing workflow-level concurrency limit once a second job existed).

**`README.md`**
- Updated the actions table to describe the lockfile-aware cache and ruff linting.

Verification: `actionlint` and `zizmor --persona=pedantic` both ran clean (exit 0, "No findings to report") after one fix cycle for the two zizmor findings (missing concurrency, template injection).
