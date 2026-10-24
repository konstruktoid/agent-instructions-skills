The audit search now has `--limit`, `--offset` and `--since`, and `--action` is optional. `--sort` and `--direction` still work. Ruff check, ruff format and ty all pass. I ran the CLI by hand against an empty database to check it starts and rejects a bad `--sort`. I didn't test pagination, `--since` or `--action` omitted against rows, and the repo has no test suite.

- **`--limit` and `--offset`:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative.
- **`--since`:** it takes an ISO date or datetime, and a malformed value is rejected. It matches rows whose `ts` is at or after the value. That comparison is on the text in `ts`, so it assumes `ts` is stored as ISO text.
- **`--action`:** leave it out and the search returns every action for the actor.
- **`--sort` and `--direction`:** `--sort` accepts any of the five columns (`id`, `actor`, `action`, `target`, `ts`), and `--direction` takes `asc` or `desc` in any case. Anything else is rejected with a clear error. Ordering now also breaks ties by `id`, so pages stay stable.
- **Query building:** the query now passes actor, action, date, limit and offset to SQLite as bound parameters. The old `--sort` and `--direction` values went straight into the SQL text, so they allowed SQL injection. They are now checked against fixed lists.
- **Docs:** the `--help` text and the README option list are updated, and the README now has a paging example.

`quote_literal` in `filters.py` is no longer used by the search. I left it in place.

The changes are in `src/auditlog/search.py`, `src/auditlog/filters.py` and `README.md`. Nothing is committed. Running the checks left an untracked `src/auditlog/__pycache__/` directory.
