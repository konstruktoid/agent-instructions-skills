The audit log search now has `--limit`, `--offset` and `--since`. `--action` is optional, and `--sort` and `--direction` work on every column of the audit table. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no test suite, so I also ran the CLI by hand against a small SQLite file. `--since`, sorting by `target`, and `--limit` with `--offset` returned the expected rows. A malicious `--sort` value and a bad `--since` value were both rejected with a usage error.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative. I added the 1000 cap myself, so say if you want a different ceiling.
- **`--since`:** it takes an ISO 8601 date or datetime and returns rows whose `ts` is at or after it. It validates the value and rejects anything that isn't a valid ISO date.
- **`--action`:** leave it out and the search matches every action for the actor.
- **Sorting:** `--sort` accepts `id`, `actor`, `action`, `target` or `ts`, and `--direction` accepts `asc` or `desc`. Both are checked against fixed lists in `auditlog.filters`, because a column name can't be passed as a query parameter. Ties are broken by `id` in the same direction, so pages stay stable.
- **Docs:** the CLI `--help` text and the README now describe every option, with a second usage example.

I rewrote the query to use bound parameters for every value instead of building it from quoted strings. That made `quote_literal` unused, so I removed it from `filters.py`.

Previously the CLI passed any `--sort` or `--direction` text straight into the SQL. Now an invalid value is a usage error.
