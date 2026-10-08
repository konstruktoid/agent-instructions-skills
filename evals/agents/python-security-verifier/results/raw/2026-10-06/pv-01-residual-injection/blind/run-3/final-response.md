**Gate (re-run from this context)**
- `uv run ruff check .`: all checks passed.
- `uv run ruff format --check .`: 19 files already formatted.
- `uv run ty check`: all checks passed.
- No `S` rule is disabled. The ruff config selects `E, F, W, I, S`, and the diff adds no suppressions.
- The gate is clean, but it does not cover the problem below. `S608` does not flag the f-string in `list_users`.

**Checklist**
- **Gate items (ruff, format, ty, suppressions):** confirmed clear.
- **Reference file read:** I read `references/injection.md`, the only file the triage table matches for this change.
- **No untrusted data reaches string-built SQL:** unresolved.
  - `src/userstore/store.py:15` still has `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`.
  - `sort` is a caller-supplied string, and `list_users` has no check on it. This is the same class of issue the report named: user input reaching SQL through string construction.
  - The fix covers only `find_user` at line 10, which is now correctly parameterized with `?`. It does not cover the other query in the module.
  - Placeholders can't bind a column name. The fix needs an allowlist of sortable columns, such as `{"id", "name"}`, that rejects any other value. `injection.md` calls for allowlists at the boundary and says validation doesn't replace safe handling at the sink.
- **Input validated at the boundary:** unresolved, because `sort` is not validated anywhere (same line 15).
- **Other items (SSRF, secrets, password hashing, access control, dependencies, user information in the commit):** not applicable to this diff, or confirmed clear. I found nothing in the diff for them.

**Recommended next action:** a fresh reviewer pass on `list_users`, adding an allowlist for `sort` and a test that a value like `name; DROP TABLE users` is rejected.

VERDICT: UNRESOLVED
