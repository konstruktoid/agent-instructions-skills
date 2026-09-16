Pagination, `--since`, optional `--action`, and injection resistance all behave correctly (empty result for the quote-injection actor, as expected since no such literal actor exists — no rows leaked).

**Files changed:**
- `src/auditlog/filters.py` — replaced string-literal quoting with an allow-list validated `order_clause`; added `SORT_COLUMNS`, `DIRECTIONS`, `DEFAULT_LIMIT`
- `src/auditlog/search.py` — parameterized `actor`/`action`/`since`/`limit`/`offset` via `?` placeholders instead of string interpolation, made `--action` optional, added `--since`, `--limit`, `--offset`
- `README.md` — documented the new flags and defaults

**Note on scope:** the original code built the whole query via string interpolation (`quote_literal` for values, raw f-string for sort/direction) — a SQL injection vector. Since I was already touching `--sort`/`--direction` handling and adding new user-supplied fields, I fixed this to use parameter binding for values and an allow-list for the column/direction identifiers (which SQLite can't bind as parameters), rather than extending the unsafe pattern. Flagging this since it's a deviation from just adding features — happy to discuss if you wanted the injection fix scoped separately.

`ruff check` and `ty check` both pass. Verified pagination, `--since`, optional `--action`, and injection attempts manually against a seeded SQLite DB (cleaned up after).
