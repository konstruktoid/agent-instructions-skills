The audit search now has `--limit`, `--offset` and `--since`, and `--action` is optional. `uv run ruff check .`, `ruff format --check .` and `ty check` all pass. The repository has no tests, so I checked behaviour with a throwaway SQLite database. It gave the expected rows for the default search, `--since` with a sort and limit, and the three rejected inputs below.

- **Pagination:** `--limit` defaults to 50 and must be 1–1000. `--offset` defaults to 0 and can't be negative. The query adds `id` as a tie-breaker so pages stay stable.
- **`--since`:** it accepts an ISO date or datetime and keeps rows whose `ts` is at or after it. It compares as text, which works for ISO-formatted `ts` values. An invalid date is rejected with a usage error.
- **`--action`:** leave it out and the search matches every action for that actor.
- **`--sort` and `--direction`:** these still work. `--sort` accepts any audit column (`id`, `actor`, `action`, `target`, `ts`), and `--direction` accepts `asc` or `desc`. Anything else is rejected at the CLI and in `order_clause`. A value like `ts; drop table audit` is refused.
- **Query building:** I replaced the string-built SQL with `?` parameters. The old `quote_literal` helper is gone, since nothing uses it any more. The sort column and direction are the only parts that can't be parameters, so they are checked against fixed lists.
- **Docs:** the CLI help text and the README describe all the options, with a pagination example.

The changes are in `src/auditlog/search.py`, `src/auditlog/filters.py` and `README.md`. I haven't committed anything. There is an untracked `src/auditlog/__pycache__/` directory from running the code, and the repo has no `.gitignore` for it.
