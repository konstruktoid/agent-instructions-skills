# tests

Empty on purpose. The checks moved to `src/ledger/_tests/` and are named
`check_*`, which is what `pyproject.toml` collects. Anything added here is not
picked up by `uv run pytest` and will not run in CI.
