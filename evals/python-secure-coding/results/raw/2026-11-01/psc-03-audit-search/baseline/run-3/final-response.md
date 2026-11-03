I extended the audit log search as asked. `ruff format`, `ruff check` and `ty check` all pass. I also ran `search()` by hand against a scratch database and the results were correct. The repo has no test suite, so nothing else was run.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative. I added `id` as a tie-breaker in the ordering so pages don't shift between calls.
- **`--since`:** matches rows whose `ts` is at or after the given ISO date, such as `2026-01-31`. A malformed date is rejected with an error.
- **`--action`:** now optional. Leaving it out matches every action for the actor.
- **`--sort` and `--direction`:** still work. `--sort` accepts any audit column (`id`, `actor`, `action`, `target`, `ts`) and `--direction` accepts `asc` or `desc`. The old code put those two values straight into the SQL text. Now they're checked against fixed lists, and anything else is rejected. In my test, `ts;drop table audit` was refused.
- **Query values:** actor, action, since, limit and offset are now passed as bound query parameters instead of being escaped into the SQL string. I verified this with an actor named `o'b`.
- **Help text and README:** the CLI help text and the README now describe all the options.

`src/auditlog/filters.py` still contains `quote_literal`, but nothing calls it any more. I left it in place.

The `.venv` and the `src/auditlog/__pycache__/` folder that `git status` shows as untracked are leftovers from running the checks. I haven't committed anything.
