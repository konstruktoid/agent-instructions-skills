The audit log search now has `--limit`, `--offset` and `--since`, and `--action` is optional. `uv run ruff format`, `uv run ruff check .` and `uv run ty check` all pass. I also ran a quick manual check against a throwaway database: the default search, an action plus `--since` filter, paging with a sort, and the rejection cases all behaved as expected. The repository has no test suite, so nothing beyond those checks ran.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative. Ordering now also sorts by `id`, so pages stay stable when rows tie on the sort column.
- **`--since`:** it takes an ISO 8601 date or datetime and matches rows where `ts` is at or after it. Anything that isn't a valid ISO date is rejected with an error.
- **`--action`:** leaving it out matches every action for the actor.
- **`--sort` and `--direction`:** these still work. `--sort` accepts any column of the audit table (`id`, `actor`, `action`, `target`, `ts`), and `--direction` accepts `asc` or `desc`. Anything else is rejected, both on the command line and in `search()` itself.
- **Docs:** the CLI help text and the README describe every option.

I changed how queries are built, which you didn't ask for. The old code built SQL by escaping quotes. Since `--sort` and `--direction` go straight into an `ORDER BY`, I made two changes:
- **Values:** actor, action, since, limit and offset are now passed as bound parameters.
- **Sort and direction:** these are checked against fixed lists of allowed values.

I removed `quote_literal` from `filters.py` because nothing uses it any more.

The changes are in `src/auditlog/search.py`, `src/auditlog/filters.py` and `README.md`. Nothing is committed.
