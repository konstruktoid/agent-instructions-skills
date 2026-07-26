Done. Summary of changes:

- **`src/auditlog/search.py`**: `--action` is now optional (matches all actions for an actor when omitted); added `--limit`/`--offset` (defaults 50/0) and `--since` (ISO date, inclusive); results ordered by `ts DESC`. Also switched the query from string concatenation to parameterized SQL, fixing a SQL injection vulnerability in the original code.
- **`README.md`**: documented the new flags and defaults.
- Verified with `uv run ruff check .` and `uv run ty check .` (both pass), plus a manual smoke test confirming ordering, pagination, the optional-action/since filters, and that injection attempts no longer alter query semantics.
