The audit log search now has `--limit`, `--offset` and `--since`, and `--action` is optional. `ruff format --check`, `ruff check` and `ty check` all pass. The repo has no test suite, so I also ran a few manual queries against a throwaway SQLite database, and they behaved as expected.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0. Ties on the sort column are broken by `id`, so pages don't shuffle between calls.
- **`--since`:** takes an ISO date or datetime and returns rows with `ts` at or after it. A bad value fails with a usage error. The comparison is on `ts` as text, so it only works if stored timestamps are ISO formatted.
- **`--action`:** omit it to match every action for the actor.
- **`--sort` and `--direction`:** still work. `--sort` accepts `id`, `actor`, `action`, `target` or `ts`, and `--direction` accepts `asc` or `desc`.
- **Help and README:** the CLI help text and the README now describe every option, with examples.

I also changed how queries are built, and that goes beyond what you asked. The old code put `--sort` and `--direction` straight into the SQL, so a crafted value could inject SQL. Values are now bound as query parameters. The sort column and direction are checked against fixed lists, because column names can't be bound as parameters. Because the values are bound, I removed `quote_literal`, which nothing used any more.

`search()` now takes `action`, `limit`, `offset` and `since` as optional arguments and raises `ValueError` for an invalid sort, direction, limit or offset.

The run also left an untracked `src/auditlog/__pycache__/` directory.
