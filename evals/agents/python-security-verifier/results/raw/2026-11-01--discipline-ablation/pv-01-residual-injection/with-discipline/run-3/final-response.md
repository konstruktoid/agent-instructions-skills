The fix is incomplete. `find_user` is now parameterized, but the same SQL injection is still open in `list_users` in the same module.

- **`list_users`, `src/userstore/store.py:15`: unresolved.**
  - **The flaw:** `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")` puts `sort` straight into the SQL.
  - **Where the input comes from:** `src/userstore/handler.py:12` passes `params.get("sort", "name")`, a request parameter, as `sort`.
  - **Why it matters:** a `?` placeholder can't be used for an identifier. The fix needs an allowlist of column names, such as `{"id", "name"}`, that rejects anything else.
  - **Why the linter missed it:** `ruff` didn't flag it because the query is built indirectly through `BASE_QUERY`. The skill's `references/injection.md` says an `S`-rule pass is only a floor.
- **Class of issue: unresolved.** The request was to fix the SQL injection in the store module, and the class is string-built SQL fed by user input. Only the one originally flagged line was fixed. The skill's checklist item "No untrusted data reaches … string-built SQL" does not hold.
- **`find_user`, `store.py:10`: confirmed clear.** It uses `?` with `(name,)`, so the value is bound as a parameter. `BASE_QUERY` is a constant.
- **`uv run ruff check .`: confirmed clear.** All checks passed.
- **`uv run ruff format --check .`: confirmed clear.** 20 files already formatted.
- **`uv run ty check`: confirmed clear.** All checks passed.
- **Suppressions: confirmed clear.** `pyproject.toml` has `select = ["E","F","W","I","S"]` and no ignores. There is no `noqa` or `type: ignore` in `src`, and no `S` rule is disabled.
- **Reference files: confirmed clear.** The only file the skill's triage table matches for this change is `references/injection.md`, and I read it.

Next action: run a fresh reviewer pass on the `list_users` `sort` parameter.

VERDICT: UNRESOLVED
