The fix is incomplete: `list_users` in the same module still has SQL injection.

**Confirmed clear (I re-ran these myself):**
- `uv run ruff check .` passes.
- `uv run ruff format --check .` passes (19 files already formatted).
- `uv run ty check` passes.
- `pyproject.toml` line 15 selects `["E","F","W","I","S"]`. No `S` rule is disabled, and no new suppressions appear in the diff.
- `find_user` (`store.py:10`) now binds `name` as a `?` parameter. The `BASE_QUERY` interpolation is a constant, so that line is sound.

**Unresolved:**
- **Injectable sink:** `src/userstore/store.py:15` is `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`. `sort` goes straight into the SQL string.
- **Reachable from user input:** `handler.py:12` passes the request's `sort` query parameter to `list_users` unchanged, and `README.md:5` says the same. An attacker can send something like `sort=name; ...` or a subquery in `ORDER BY` and run their own SQL. That fails the checklist item "No untrusted data reaches … string-built SQL".
- **Why ruff missed it:** the `S` rules did not flag it, which is the "floor, not proof" case `injection.md` warns about.
- **Wrong class of fix:** the request named the SQL injection in the store module, and the fix covered only the one line originally flagged. Placeholders can't bind a column name, so `list_users` needs an allowlist of sortable columns, with a request for any other column rejected at the boundary. `injection.md` prefers allowlists over denylists.

**Next action:** run a fresh reviewer pass on `list_users`, with an allowlist for `sort` and a test that a malicious `sort` value is rejected.

VERDICT: UNRESOLVED
