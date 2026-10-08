**Per-item verdicts**

- **`ruff check`, `ruff format --check`, `ty check`:** confirmed clear. I re-ran all three through `uv run` and each passed. The `.venv` I created is a side effect of that run.
- **No `S`-rule disabling or new suppressions:** confirmed clear. `pyproject.toml` selects `E, F, W, I, S` with no ignores, and the diff adds no `noqa`.
- **`find_user` (the line originally flagged):** confirmed clear. `store.py:10` now passes `name` as a bound `?` parameter. The f-string only inserts the constant `BASE_QUERY`.
- **Fix covers the whole class of SQL injection, not just the flagged line:** **unresolved**.
  - `src/userstore/store.py:15` still has `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`, which is string-built SQL.
  - `sort` comes straight from the request. `src/userstore/handler.py:12` passes `params.get("sort", "name")` to it with no validation.
  - A caller can inject through the `ORDER BY` clause, for example with a subquery expression or a boolean-blind ordering.
  - `ruff` and `ty` pass on this line anyway, so the clean run doesn't show it is safe. `injection.md` says an `S`-rule pass is a floor, not proof.
  - The fix needs the `sort` value checked against an allowlist of column names, such as `{"id", "name"}`. SQL parameters can't bind identifiers. Invalid values should be rejected, not rewritten.
- **Untrusted input validated at the boundary and no string-built SQL from untrusted data:** unresolved, for the same `list_users` / `handler.py` path.
- **`injection.md` read and applied:** confirmed clear. It was the only reference file the triage table matched for this change.
- **Items that don't apply to this diff:** confirmed clear. The diff doesn't touch SSRF, secrets, password hashing, authorization, dependencies or user and system information.

**Next action:** run a fresh reviewer pass on `list_users` and its `handler.py` caller. Add an allowlist for `sort` and a test that an unlisted value is rejected.

VERDICT: UNRESOLVED
