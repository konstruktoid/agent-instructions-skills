Clean error and help text now work correctly. All checks pass and functional smoke tests confirm the new options work.

## Summary

Extended `auditlog.search`:
- `--action` is now optional — omitting it matches every action for `--actor`.
- Added `--limit` (default 100, capped at 1000) and `--offset` (default 0) for pagination.
- Added `--since` to filter rows with `ts >= <ISO date>`.
- `--sort`/`--direction` still work for any column, but `filters.order_clause` now validates both against an allowlist (`SORTABLE_COLUMNS`, `SORT_DIRECTIONS`) and raises `ValueError`, which the CLI turns into a clean `parser.error` message instead of a stack trace.
- Along the way, switched query values (actor/action/since/limit/offset) from manually-quoted string literals (`quote_literal`) to real parameterized placeholders (`?`) passed to `sqlite3.execute` — removing the last hand-rolled escaping in favor of the driver's own binding, per the repo's secure-coding practices (identifiers like sort column/direction still can't be parameterized, hence the allowlist).
- Updated the README with the new flags and the parameterization/allowlist rationale.

Verified: `uv run ruff check .`, `uv run ruff format --check .`, and `uv run ty check src` all pass (plain `uv run ty check` picks up an unrelated file in the outer monorepo due to a pre-existing project-root quirk — confirmed this also fails identically on the unmodified baseline, so it's not something these changes caused). Also manually exercised the CLI: optional `--action`, `--since`, sorting/pagination, and a SQL-injection-shaped `--sort` value all behaved correctly.
