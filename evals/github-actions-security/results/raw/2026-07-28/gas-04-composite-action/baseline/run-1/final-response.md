All four changes are done and both YAML files validated with `yaml.safe_load`:

1. **`actions/setup-toolchain/action.yml`** — cache key now includes `hashFiles('uv.lock')`; added `Install ruff` + `Lint with ruff` steps after the toolchain install.
2. **`.github/workflows/ci.yml`** — `test` job now uses a `strategy.matrix.os: [ubuntu-latest, windows-latest]`, so the same action and test suite run on both platforms.
3. **`README.md`** — updated the Actions table entry and added a CI section describing the matrix.

No test suite exists to run in this fixture repo (no Python files, no `uv.lock`), so verification was limited to YAML validity — nothing else to execute here.
