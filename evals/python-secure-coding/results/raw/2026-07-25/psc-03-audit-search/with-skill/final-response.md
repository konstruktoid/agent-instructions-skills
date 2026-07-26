No test suite exists in this repo — ruff and ty are the only configured checks, and both pass cleanly.

I also fixed a pre-existing SQL injection vulnerability along the way: the old code concatenated `actor`/`action` directly into the query string, so I switched to parameterized placeholders while adding the new filters.

Summary of changes:
- `src/auditlog/search.py`: `search()` now takes optional `action`, `since`, and `limit`/`offset` (defaults 50/0), builds the query with `?` placeholders, and orders by `ts DESC`. CLI's `--action` is no longer required; added `--since`, `--limit`, `--offset` with help text.
- `README.md`: documented the optional `--action`, `--since`, and pagination flags.
- `uv run ruff check .`, `ruff format --check .`, and `ty check` all pass.
