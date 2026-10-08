The audit log search now has `--limit`, `--offset` and `--since`, and `--action` is optional. `ruff check`, `ruff format --check` and `ty check` all pass. I also ran it by hand against a throwaway SQLite database, and filtering, paging, sorting and the invalid inputs all behaved as expected. I didn't add automated tests, since the repo has none. The `__pycache__` directory from that run shows as untracked in git status. I haven't committed anything.

- **Pagination:** `--limit` defaults to 50 and must be between 1 and 1000. `--offset` defaults to 0 and can't be negative. Ties in the sort are broken by `id`, so consecutive pages don't overlap.
- **`--since`:** this takes an ISO 8601 date or datetime and keeps rows with `ts >= since`. An invalid value is rejected as a usage error.
- **`--action`:** leaving it out matches every action for the actor.
- **`--sort` / `--direction`:** these still work and now accept any audit column (`id`, `actor`, `action`, `target`, `ts`) with `asc` or `desc`. The CLI limits them to those choices, and `order_clause` checks them again and raises `ValueError` otherwise.
- **SQL injection:** the old query built its `WHERE` clause with a quote-escaping helper, and `--sort` was pasted into `ORDER BY` unchecked, which allowed injection. Values are now bound as `?` parameters, and `quote_literal` is removed. Column names can't be bound as parameters, so they are checked against the allowlist instead. A quick check with a SQL-injection string as the actor returned no rows, and a malicious sort value was rejected.
- **Docs:** the CLI help text covers every option, and the README now lists each option and its default.

`ts` is stored as text, so `--since` relies on ISO timestamps sorting correctly as strings. That holds as long as stored values are ISO formatted.
