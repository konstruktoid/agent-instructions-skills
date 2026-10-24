`find_user` is fixed, but the SQL injection the report named is still open in the same module, so the verdict is unresolved.

**Tooling, re-run here:**
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed.
- `uv run ty check` passed.
- `pyproject.toml` selects `S` and has no `ignore` entries, so no `S` rule was disabled.
- The diff adds no suppressions.

**Checklist items:**
- **`find_user` parameterization: confirmed clear.** `store.py:10` now passes `name` as a bound `?` parameter. `BASE_QUERY` is a constant, so the f-string interpolates nothing user-controlled.
- **Class of issue, no string-built SQL reaches user input: unresolved.** `store.py:15` is `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`. `handler.py:12` passes `params.get("sort", "name")`, which is request-controlled, straight into that call. Because `sort` lands in the SQL text, it is injectable (for example `name; ...` or a subquery expression). The fixer's claim that "no user input is interpolated into SQL anywhere in the module" is false. Ruff's `S608` did not flag it, which matches the reference's warning that a lint pass is only a floor. `references/injection.md` requires parameterized queries and allowlist validation; this line has neither.
  - **Next step:** a column name cannot be bound as a `?` parameter, so `sort` needs an allowlist of column names (for example `{"id", "name"}`) that rejects anything else. Do it at the boundary in `list_users` or `handler`, and add a test for a hostile `sort` value.
- **Boundary validation of untrusted input: unresolved** for the same `sort` parameter. Nothing validates it.
- **Other checklist items:** not applicable to this change. It touches no secrets, crypto, deserialization, SSRF, access control, dependencies or committed user data.

**Next action:** a fresh reviewer pass to fix `list_users` and its `sort` input.

VERDICT: UNRESOLVED
