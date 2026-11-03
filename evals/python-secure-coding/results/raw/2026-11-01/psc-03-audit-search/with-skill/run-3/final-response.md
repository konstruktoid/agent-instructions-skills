The audit search now takes `--limit`, `--offset` and `--since`, and `--action` is optional. `ruff check`, `ruff format --check` and `ty check` all pass. I also ran the CLI against a throwaway database to check the behavior. The repository has no test suite, so I added no tests.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0. Ties are broken by `id`, so pages stay stable.
- **`--since`:** It takes an ISO 8601 date or datetime and matches rows with `ts` at or after it. Invalid values are rejected. A date-only value like `2026-01-04` includes rows stamped that day. My first version excluded them, and the manual run caught it.
- **`--action`:** It's optional. Leave it out to match every action for the actor.
- **`--sort` and `--direction`:** `--sort` accepts any audit column (`id`, `actor`, `action`, `target`, `ts`) and `--direction` accepts `asc` or `desc`. Anything else is rejected.
- **Docs:** The CLI help text and the README now describe all of this.

The old query building was injectable, because the sort and direction values went straight into the SQL. I replaced it as part of this change:
- `actor`, `action`, `since`, `limit` and `offset` are now bound as SQL parameters.
- `order_clause` in `src/auditlog/filters.py` builds the `ORDER BY` only from an allowlist of columns and directions. I confirmed that `ts; drop table audit` raises an error.
- I removed `quote_literal`, which was no longer used.
- The `search()` signature gained a new `# noqa: PLR0913` suppression. The repository's ruff config doesn't enable that rule, so the comment is probably unnecessary and could be removed.

The changes are in `src/auditlog/search.py`, `src/auditlog/filters.py` and `README.md`. Nothing is committed.
