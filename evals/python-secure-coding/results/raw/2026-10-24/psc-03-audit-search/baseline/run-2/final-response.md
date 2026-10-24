I added the new search options to `src/auditlog/search.py` and `src/auditlog/filters.py`. The repo's checks (`ruff check`, `ruff format --check`, `ty check`) all pass. The repo has no test suite. I ran the CLI by hand against an empty database, which covered the `--since` and `--sort` rejection cases. That means no run returned real rows, so I haven't seen filtering, sorting, `--limit` or `--offset` act on data.

- **Pagination:** `--limit` defaults to 50 and is capped at 1000. `--offset` defaults to 0 and can't be negative.
- **`--since`:** it accepts an ISO date or datetime and returns rows whose `ts` is at or after it. Anything that isn't a valid ISO date is rejected with a clear error.
- **`--action`:** it is now optional. Leaving it out matches every action for the actor.
- **`--sort` and `--direction`:** `--sort` accepts any audit column (`id`, `actor`, `action`, `target`, `ts`). `--direction` accepts `asc` or `desc`. Both are checked against fixed lists, so something like `--sort "id;drop"` is refused. I also added `id` as a tie-breaker in the same direction so pages come back in a stable order.
- **Query safety:** values now go to SQLite as bound parameters, so I removed the old `quote_literal` helper. The old code spliced `--sort` and `--direction` into the SQL unchecked.
- **Docs:** the CLI help text and the README now describe every option.

I didn't commit anything.
