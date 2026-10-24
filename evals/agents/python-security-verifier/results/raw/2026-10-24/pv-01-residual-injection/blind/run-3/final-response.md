The fix is incomplete. SQL injection is still possible in `list_users`, in the same module the report named.

**Unresolved**
- `src/userstore/store.py:15` still builds SQL from untrusted input: `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`.
- `src/userstore/handler.py:12` passes `params.get("sort", "name")`, which comes from the request, straight into that `sort` argument.
- An ORDER BY column name can't be bound as a `?` parameter. The `injection.md` rule on SQL construction requires an allowlist at the boundary instead, for example a fixed set like `{"name", "id"}` that rejects anything else. Neither exists.
- The request named the class of issue, user input reaching SQL in the store module. The commit fixed only `find_user` (line 10), which is now correctly parameterized with `?` and `(name,)`.
- Ruff's `S608` rule didn't flag line 15, so a clean lint run doesn't show it is safe.

**Confirmed clear**
- `uv run ruff check .`: all checks passed.
- `uv run ruff format --check .`: 20 files already formatted.
- `uv run ty check`: all checks passed.
- Suppressions: `pyproject.toml` selects `["E", "F", "W", "I", "S"]`, and I found no ignores or `S` rules disabled in the diff.
- `find_user` fix itself, as noted above.

**Not applicable**
- No dependencies changed, and the diff touches no secrets, crypto, SSRF or access-control code.

**Next action:** a fresh reviewer pass to add an allowlist for `sort` in `list_users`, or at the boundary in `handler.py`, and then rerun the gate.

VERDICT: UNRESOLVED
