Changes complete and YAML-validated. Files changed:

- `actions/setup-toolchain/action.yml` — added `runner.os` + `hashFiles('uv.lock')` to the cache key, added `pip install ruff` + `ruff check .` steps after toolchain install.
- `.github/workflows/ci.yml` — added `test-windows` job (`windows-latest`) running the same composite action and `python -m pytest`.
- `README.md` — updated action description, added a CI job/platform table.

Note: this repo has no `uv.lock`, `pyproject.toml`, or Python source/tests — `hashFiles('uv.lock')` will evaluate to empty string and `ruff check .` / `pytest` will fail if actually run, since there's nothing to lint or test. I didn't fabricate a lockfile or test suite since none was requested; flag if you want stub files added.

You'll want to `/clear` before starting anything unrelated.
