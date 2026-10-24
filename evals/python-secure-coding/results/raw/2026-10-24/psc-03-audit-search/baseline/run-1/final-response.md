The audit search now takes `--limit`, `--offset` and `--since`, and `--action` is optional. `ruff check`, `ruff format --check` and `ty check` all pass. The repo has no tests, so I also ran a quick manual check against a scratch database. It confirmed the `--since` filter, `--limit`/`--offset` paging and the rejection of a bad sort column.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative. Out-of-range values give a normal argparse error.
- **`--since`:** it accepts an ISO date or datetime and returns rows with `ts` at or after it. A value that isn't a valid ISO date is rejected.
- **`--action`:** leaving it out matches every action for the actor.
- **Sorting:** `--sort` accepts any audit column (`id`, `actor`, `action`, `target`, `ts`) and `--direction` accepts `asc` or `desc`. Ties are broken by `id`, so pages stay stable.
- **Docs:** I updated the CLI help text and the README.

I also fixed an existing SQL injection hole. `--sort` and `--direction` were pasted straight into the query. They're now checked against fixed lists. The actor, action, since, limit and offset values are now passed as bound query parameters. That made `quote_literal` unused, so I removed it from `filters.py`.

I deleted the `.venv` that `uv run` created and the `__pycache__` directory from my manual run, so the working tree contains only the three modified files.
