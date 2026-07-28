Clean. I'm not committing since that wasn't requested — leaving the changes staged in the working tree for review.

## Summary

Extended `auditlog.search` with pagination, date filtering, and an optional action filter, while fixing a latent SQL-injection surface along the way:

- **`--limit`/`--offset`** — default 50 / 0, validated non-negative, applied via bound `LIMIT ?/OFFSET ?`.
- **`--since`** — optional ISO-date filter (`ts >= ?`), bound as a parameter.
- **`--action`** — now optional; omitting it matches every action for `--actor`.
- **`--sort`/`--direction`** — still work and now accept any audit column, but `filters.order_clause` validates both against an allowlist (`id/actor/action/target/ts`, `asc/desc`) before building the clause, since identifiers can't be bound as SQL parameters.
- Replaced the old hand-rolled `quote_literal` string-escaping (a fragile SQL-injection-prone pattern) with real parameterized queries for `actor`/`action`/`since`/`limit`/`offset`.
- Updated CLI `--help` text and the README to document all new flags and the validation model.
- Added `tests/test_search.py` (stdlib `unittest`, no new dependency) covering pagination, optional action, `--since`, arbitrary-column sort, and rejection of injection attempts via `--sort`/`--direction`/negative limit/offset.

Verified: `ruff check`, `ruff format --check`, `ty check` (scoped to `src tests` — the bare `ty check` picks up an unrelated outer monorepo `pyproject.toml` and fails on that repo's own `scripts/check_skills.py`, pre-existing and reproducible on the original baseline via `git stash`), and the full test suite (9/9) all pass. Manually exercised the CLI including a `--sort "ts; DROP TABLE audit"` injection attempt, which is now rejected with `ValueError`.
