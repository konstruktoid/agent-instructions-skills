I added the pagination, date filter and optional `--action` to the audit log search, and updated the README. `ruff check`, `ruff format --check` and `ty check` all pass.

I also ran the CLI against a throwaway database, outside the repo:
- **`--since`:** `--actor a --since 2026-01-01` returned only the row dated 2026-01-02.
- **Quoting:** an actor containing an apostrophe (`a'b`) was found correctly.
- **Sorting:** `--sort target --direction ASC` worked. `--sort "ts;drop"` was rejected with a clear error.

I added no tests.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative. Ties in the ordering are broken by `id`, so pages don't shift between calls.
- **`--since`:** it takes an ISO 8601 date or datetime and returns rows with `ts` at or after it. This is a plain text comparison on `ts`, so it only behaves correctly if `ts` values are stored in ISO format.
- **`--action`:** it is now optional. Leave it out to match every action for the actor.
- **`--sort` and `--direction`:** they still work. `--sort` accepts any column of the table (`id`, `actor`, `action`, `target`, `ts`) and `--direction` accepts `asc` or `desc`, in either case. The old code put the sort value straight into the SQL, so I check both against fixed lists and reject anything else.
- **Queries:** values (actor, action, since, limit, offset) are now passed to SQLite as bound parameters instead of being built into the SQL string. I removed `quote_literal` from `filters.py` because nothing uses it any more.
- **Help text and README:** each option has `--help` text with its default, and the README lists every option with an example.

`search()` and `order_clause()` now raise `ValueError` on a bad sort column or direction, so code calling them directly will see that. Running the checks also left an untracked `src/auditlog/__pycache__/` folder in the repo.
