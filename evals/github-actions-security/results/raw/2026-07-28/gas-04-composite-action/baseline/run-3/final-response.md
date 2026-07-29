Both YAML files parse correctly. Everything is in order.

**Summary of changes:**
- `actions/setup-toolchain/action.yml`: added a `Lint with ruff` step after toolchain install, and the cache key now includes `${{ hashFiles('**/uv.lock') }}` so lockfile changes invalidate the cache.
- `.github/workflows/ci.yml`: added a `test-windows` job (renamed jobs to "Test (Ubuntu)"/"Test (Windows)") running the same composite action and `pytest` suite on `windows-latest`.
- `README.md`: updated the actions table to mention linting/lockfile-hashed cache, and added a CI matrix table listing both platforms.

Note: no `uv.lock` or `pyproject.toml` exists in this fixture repo yet, so `hashFiles('**/uv.lock')` will currently evaluate to an empty string (cache key still works, just without lockfile-based invalidation until that file is added).
