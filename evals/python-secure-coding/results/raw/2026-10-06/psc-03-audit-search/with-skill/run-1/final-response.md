The audit log search now has pagination, a date filter and an optional action. `ruff check`, `ruff format --check` and `ty check` all pass. I also ran the CLI against a throwaway SQLite database. A default search, `--since` with `--sort`, `--direction` and `--limit`, and an injection-style `--sort` all behaved as expected. The repository has no test suite, so I didn't add tests. Nothing is committed.

- **`--limit` and `--offset`:** `--limit` defaults to 50 and accepts 1–1000. `--offset` defaults to 0 and must be 0 or more. Ties in the sort are broken by `id`, so pages stay stable as you step through them.
- **`--since`:** It takes an ISO 8601 date or datetime and returns rows whose `ts` is at or after it. A bad value is rejected with a clear error.
- **`--action`:** It is now optional. Leave it out and the search matches every action for the actor.
- **`--sort` and `--direction`:** `--sort` accepts any audit table column (`id`, `actor`, `action`, `target`, `ts`). `--direction` accepts `asc` or `desc` in any case.
- **Docs:** The CLI help text and the README now describe every option.

**Security changes:** The old code built SQL by escaping strings, and `--sort` and `--direction` went straight into `ORDER BY`. That meant a crafted `--sort` could inject SQL. Values are now bound as `?` parameters. `--sort` and `--direction` are checked against allowlists in `auditlog.filters`, and the CLI rejects anything else. I removed `quote_literal` since nothing uses it any more.

`order_clause` now raises `ValueError` for an unknown column or direction. Any other caller of it will see that change.
