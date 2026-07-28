Done. Summary of changes:

- **`src/auditlog/search.py`**: `--action` is now optional (matches all actions for the actor when omitted); added `--since` (ISO date filter, validated with `date.fromisoformat`), `--limit` (default 50) and `--offset` (default 0) for pagination. Switched query construction from manual string quoting to parameterized bind values (`?` placeholders) for `actor`/`action`/`since`/`limit`/`offset`, and added help text for every flag.
- **`src/auditlog/filters.py`**: `order_clause` now validates `sort` against the audit table's actual columns and `direction` against `asc`/`desc` before interpolating them (they can't be parameterized), raising `ValueError` on anything else — closes off SQL injection via `--sort`/`--direction`. Removed the now-unused `quote_literal` in favor of bound parameters.
- **`README.md`**: documented the new optional `--action`, `--since`, `--limit`/`--offset`, and the sort/direction allow-list.

Verified manually against a temp SQLite DB: optional-action search, `--since` filtering, custom sort/direction, pagination, an injection attempt via `--sort` (rejected with a clean CLI error), and an injection attempt via `--actor` (safely treated as a literal value, no rows matched). `ruff check` and `ty check` both pass.
