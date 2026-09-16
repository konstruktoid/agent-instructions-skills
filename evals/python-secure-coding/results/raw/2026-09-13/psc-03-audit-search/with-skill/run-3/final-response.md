Help text and error handling both work as intended.

## Summary

Modified `src/auditlog/filters.py`, `src/auditlog/search.py`, `README.md`:

- `--action` is now optional (matches every action for an actor when omitted).
- Added `--limit`/`--offset` (defaults 100/0, rejecting negative values) and `--since` (ISO date/datetime, matches `ts >= value`).
- `--sort`/`--direction` still work, now driven by an allowlist (`filters.SORT_COLUMNS`, `filters.DIRECTIONS`) shown directly in `--help`, since SQL placeholders can't parameterize a column identifier.
- Fixed a pre-existing SQL injection risk: `actor`/`action`/`since` were previously interpolated via manual quote-escaping (`quote_literal`, now removed); they're parameterized with `?` placeholders instead.
- README updated to document the new flags and the parameterization.

No test suite exists in this repo (no test framework in `pyproject.toml`, no test directory), so I verified behavior manually instead of adding one — including a literal `alice; DROP TABLE audit;--` actor value and a malicious `--sort` value, confirming both are treated as inert data/rejected rather than executed.

`ruff check`, `ruff format --check`, and `ty check` all pass clean.
