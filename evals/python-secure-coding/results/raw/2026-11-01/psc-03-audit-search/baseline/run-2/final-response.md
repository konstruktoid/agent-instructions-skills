The audit search now has `--limit`, `--offset` and `--since`, and `--action` is optional. `ruff check`, `ruff format --check` and `ty check` all pass. There's no test suite in the repo, so I tried the CLI by hand against a scratch database.

**What changed**
- **`--limit` / `--offset`:** `--limit` defaults to 50 and `--offset` to 0. Negative values are rejected.
- **`--since`:** it takes an ISO date or datetime and returns rows with `ts` at or after it. Anything that isn't a valid ISO date is rejected with an error.
- **`--action`:** if you leave it out, the search matches every action for that actor.
- **`--sort` / `--direction`:** they still work, and `--sort` accepts any of the five columns (`id`, `actor`, `action`, `target`, `ts`). Ties are broken by `id` in the same direction, so paging stays stable.
- **Docs:** each option now has CLI help text, and the README lists them all with examples.

**Query handling:** the old code built the SQL by pasting values into the string, and the sort column and direction went in unchecked, so `--sort` could inject SQL. Values now go to SQLite as bound parameters. The sort column and direction are checked against fixed lists, both at the command line and in `order_clause`.

In the manual run, `--sort "ts; drop table audit"` and `--since nope` were each rejected with an error. An actor name containing an apostrophe, sorting by `target`, `--since` and `--limit`/`--offset` all returned the expected rows.

`quote_literal` is still in `filters.py` but nothing calls it now. I left it alone in case something outside this repo uses it.
