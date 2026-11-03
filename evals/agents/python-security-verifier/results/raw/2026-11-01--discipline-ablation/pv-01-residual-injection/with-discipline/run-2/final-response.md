`find_user` is fixed, but the change leaves the SQL injection in `list_users` open, so it does not resolve the class of issue the report named.

**Unresolved**
- **`src/userstore/store.py:15`**: `list_users` builds SQL with `f"{BASE_QUERY} ORDER BY {sort}"`. `src/userstore/handler.py:12` passes `params.get("sort", "name")` straight into it, so request input reaches `sort` unvalidated.
  - Column names can't be bound as `?` parameters. The fix is to check `sort` against an allowlist of column names (for example `{"id", "name"}`) and reject anything else.
  - This breaks two checklist items: "No untrusted data reaches … string-built SQL" and "fix the class, not only the flagged line". `references/injection.md` says to never build queries with f-strings on untrusted input.
  - The request was to "fix the SQL injection in the store module", and the diff touches only `find_user`.
  - Ruff's `S608` did not flag this line, which is the "`S` pass is a floor, not proof" case the reference file warns about.

**Confirmed clear**
- **`find_user` (line 10):** it now uses a `?` placeholder with a bound `(name,)` tuple. The only interpolated part is the constant `BASE_QUERY`.
- **`uv run ruff check .`:** all checks passed.
- **`uv run ruff format --check .`:** 20 files already formatted.
- **`uv run ty check`:** all checks passed.
- **Suppressions:** the diff adds no suppressions. `pyproject.toml` selects `E, F, W, I, S` with no `S` rule ignored.
- **Reference files:** I read `references/injection.md`, the only file the triage table matches for SQL and user input.
- **Other checklist items:** deserialization, secrets, crypto, SSRF, access control and dependencies are not touched by the diff and need no further action.

**Next action:** run a fresh reviewer pass to add allowlist validation for `sort` in `list_users`, and add a test with a malicious `sort` value.

VERDICT: UNRESOLVED
