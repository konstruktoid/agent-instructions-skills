Done. Summary of changes:

- **`src/auditlog/search.py`**: `--action` is now optional (matches every action when omitted); added `--limit`/`--offset` (defaults 50/0, rejected if negative) and `--since` (ISO-date lower bound on `ts`). Query values (`actor`, `action`, `since`, `limit`, `offset`) are now passed as bound SQLite parameters instead of manually-escaped string literals.
- **`src/auditlog/filters.py`**: `order_clause` now validates `sort` against the real audit columns and `direction` against `asc`/`desc` before interpolating them (identifiers can't be bound parameters, so this closes off the injection path that existed via `--sort`/`--direction`). Removed the now-unused `quote_literal` helper since values go through parameterization instead.
- **`README.md`**: documents the optional `--action`, pagination flags, `--since`, the sort-column allowlist, and the switch to bound parameters.

Verified with a scratch SQLite DB: normal search, action-omitted search, `--since` filtering, `--sort`/`--direction` combined with `--limit`/`--offset`, and injection attempts via `--sort`, `--direction`, and `--actor` (all rejected or safely parameterized, table left intact). `ruff check .` and `ty check .` both pass.
