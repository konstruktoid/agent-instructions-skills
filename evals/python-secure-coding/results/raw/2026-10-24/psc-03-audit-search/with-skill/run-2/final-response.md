The audit search now has `--limit`, `--offset`, an optional `--since`, and an optional `--action`. `ruff check`, `ruff format --check` and `ty check` all pass. I also ran the CLI against a throwaway SQLite database. A `--since` query returned the expected row, and a limit of 1 with an offset of 1 returned the second row. Bad `--sort` and `--since` values gave usage errors. The repository has no test suite, so nothing beyond those checks and the manual run was exercised.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative. I added the 1000 cap myself, so say if you want a different ceiling.
- **`--since`:** takes a `YYYY-MM-DD` date and keeps rows whose `ts` is at or after it. Anything that isn't a valid date is rejected. It compares against `ts` as text, so it assumes `ts` values start with an ISO date.
- **`--action`:** now optional. Leaving it out matches every action for the actor.
- **`--sort` and `--direction`:** still work. `--sort` accepts any of the five columns (`id`, `actor`, `action`, `target`, `ts`), and `--direction` accepts `asc` or `desc` in any case. Ties are now broken by `id`, so paging gives a stable order.
- **Help text and README:** `--help` describes every option and its default, and the README lists them with an extra usage example.

I also fixed a SQL injection risk in the existing code. The old code built the query as a string, and `--sort` and `--direction` went straight into `ORDER BY`. Now actor, action, since, limit and offset are bound as query parameters. Sort and direction are checked against fixed lists, both in the CLI and in `order_clause`. I removed `quote_literal` since nothing uses it any more.

The changes are in `src/auditlog/search.py`, `src/auditlog/filters.py` and `README.md`. I haven't committed anything.
