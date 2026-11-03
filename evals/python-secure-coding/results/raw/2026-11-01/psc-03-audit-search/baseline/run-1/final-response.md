I extended the audit search with pagination, a `--since` filter and an optional `--action`. `ruff check` and `ty check` both pass. The repo has no tests, so I checked the behavior by hand against a temporary SQLite database, and it worked.

- **Pagination:** `--limit` defaults to 50 and is capped at 1000, and `--offset` defaults to 0. Negative values are rejected. Ties on the sort column are broken by `id`, so paging is stable.
- **`--since`:** it matches rows whose `ts` is at or after an ISO date or datetime. Anything that isn't a valid ISO date is rejected.
- **`--action`:** it's now optional. Leave it out to match every action for the actor.
- **`--sort` and `--direction`:** these still work, and `--sort` accepts any of the five columns (`id`, `actor`, `action`, `target`, `ts`). `--direction` is case-insensitive.
- **Docs:** the CLI help text and the README describe all the options.

**Query safety.** I changed how the query is built. The old code put the sort column and direction straight into the SQL, so a caller could inject SQL through them. Now `order_clause` in `filters.py` checks both against an allowlist and raises `ValueError` on anything else. The actor, action, date, limit and offset values are passed as bound parameters. `quote_literal` is still in `filters.py` but nothing uses it now.

Two behaviors to be aware of: `search()` raises an error on a bad sort column, and a `--limit` above 1000 is silently capped at 1000.
