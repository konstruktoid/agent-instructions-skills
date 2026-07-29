YAML validates and the diff is clean. Summary of changes:

- **`actions/setup-toolchain/action.yml`**: cache key now includes `hashFiles('uv.lock')` so lockfile changes bust the cache; added a `ruff check .` lint step after the toolchain install.
- **`.github/workflows/ci.yml`**: converted the `test` job to a `strategy.matrix` over `ubuntu-latest`/`windows-latest`, running the same action and pytest suite on both.
- **`README.md`**: updated the actions table to mention the lockfile-keyed cache and ruff lint, and added a CI section noting the two-platform matrix.
