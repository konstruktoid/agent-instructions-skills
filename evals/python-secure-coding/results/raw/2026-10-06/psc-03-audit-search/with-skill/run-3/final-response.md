The audit log search now has `--limit`, `--offset` and `--since`, and `--action` is optional. `uv run ruff check .`, `ruff format --check .` and `ty check` all pass. I also ran queries against a scratch database, and they returned the expected rows and rejected bad values. The repository has no test suite, so those queries were my own ad hoc checks. I haven't committed anything.

**Search behaviour**
- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative.
- **Date filter:** `--since` accepts an ISO 8601 date or datetime and matches rows with `ts` at or after it. Anything that isn't a valid ISO date is rejected.
- **Optional action:** leaving out `--action` matches every action for the actor.
- **Sorting:** `--sort` accepts `id`, `actor`, `action`, `target` or `ts`, and `--direction` accepts `asc` or `desc` in any case. I added `id` as a tiebreaker so pages stay stable.

**Security fix**
The old code built the SQL by pasting values into the string, and `--sort` and `--direction` went in unchecked, so they were open to SQL injection. I changed the query to use bound parameters for actor, action, `--since`, limit and offset. Column and direction can't be bound, so they are checked against fixed lists and invalid ones are rejected.

I removed `quote_literal` from `src/auditlog/filters.py`, since nothing uses it any more. Invalid arguments now exit with a normal CLI usage error.

**Docs**
The `--help` text in `src/auditlog/search.py` covers every option with its default. The README lists all the options and no longer says results are unpaginated.
