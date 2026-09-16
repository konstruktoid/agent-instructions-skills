Changed: `src/auditlog/filters.py`, `src/auditlog/search.py`, `README.md`.

- `search()` now takes optional `action`/`since`, and `limit`/`offset` (defaults 50/0); `--action` is no longer required.
- Switched query construction from `quote_literal` string-concatenation to parameterized `?` placeholders for `actor`, `action`, `since`, `limit`, `offset` — the prior manual-escaping approach was a needless injection surface for a value sink; removed `quote_literal` since it's now dead code, no other callers.
- `order_clause` now validates `sort`/`direction` against a fixed allowlist (`SORTABLE_COLUMNS`, `DIRECTIONS`) and raises `ValueError` on anything else, since SQLite placeholders can't parameterize identifiers/keywords — previously these were interpolated with no validation at all. `main()` catches that and reports it via `parser.error()`.
- `ruff check`, `ruff format --check`, `ty check` all pass. No test suite exists in this repo (no test files, no pytest dependency) so I verified behavior manually against a scratch SQLite DB, including the optional-action, `--since`, `--sort`/`--direction`, `--limit`/`--offset` paths, an injection-shaped `--sort` value (rejected), and an injection-shaped `--actor` value (safely treated as literal data, no rows matched).

Deviated from a literal "just add flags" reading of the request by also fixing the pre-existing SQL-construction pattern in the code I was already touching, per this repo's security-coding rules on parameterized queries and identifier allowlisting — flagging that since it's broader than the minimal diff.
