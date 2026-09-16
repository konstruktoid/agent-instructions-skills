Files changed: `src/auditlog/filters.py`, `src/auditlog/search.py`, `README.md`.

Summary of changes:
- `filters.py`: `order_clause` now whitelists `sort` against actual columns and `direction` against asc/desc, raising `ValueError` otherwise — the previous version interpolated both directly into SQL with no validation, which was a live injection point once sort/direction are CLI-controlled.
- `search.py`: `action` is now optional (omitting it matches every action for the actor); added `--since` (ISO date/datetime, `ts >=` filter) and `--limit`/`--offset` (defaults 50/0, bound as query parameters, not string-interpolated); `search()` builds its WHERE clause from only the conditions that were actually supplied.
- `README.md`: documents the optional `--action`, the sort/direction whitelist, `--since`, and pagination defaults.

`uv run ruff check` and `uv run ty check` both pass. I also manually seeded a SQLite DB and exercised every new flag, including an attempted injection through `--sort` and a malformed `--since` value — both are rejected with a clear CLI error rather than reaching the query.

You can `/clear` now — this task is done and self-contained.
