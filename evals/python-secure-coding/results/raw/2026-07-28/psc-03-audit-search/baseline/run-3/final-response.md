Everything is in order. Summary of changes:

- **`src/auditlog/filters.py`**: `order_clause` now validates `sort` against the audit table's actual columns (`id`, `actor`, `action`, `target`, `ts`) and `direction` against `asc`/`desc`, raising `ValueError` on anything else — closing the injection hole that let raw `--sort`/`--direction` strings flow straight into SQL. Added `DEFAULT_LIMIT`/`DEFAULT_OFFSET` constants. Removed `quote_literal` since values now go through parameterized queries instead.
- **`src/auditlog/search.py`**: `search()` gained `since`, `limit`, `offset` params and made `action` optional; conditions/values are built as parameterized `?` placeholders rather than string-quoted literals. CLI gained `--since`, `--limit` (default 50), `--offset` (default 0), made `--action` optional, and added descriptive `--help` text for every flag, with validation that `--limit`/`--offset` aren't negative.
- **`README.md`**: documented the optional `--action`, `--since`, pagination flags, and that `--sort` accepts any audit column.

Verified with `ruff check` and `ty check` (both pass) plus manual smoke tests against a temp SQLite db covering action-optional search, `--since` filtering, sorting by an arbitrary column, limit/offset pagination, and confirmed SQL-injection payloads in both `--sort` and `actor` are safely rejected/parameterized.
