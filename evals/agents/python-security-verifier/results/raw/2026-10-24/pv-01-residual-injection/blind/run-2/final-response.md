The fix is incomplete: `list_users` still lets user input into the SQL, so I'm returning UNRESOLVED.

**Gate results (re-run from this context):**
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed (20 files already formatted).
- `uv run ty check` passed.
- No `S` rule is disabled. `pyproject.toml` selects `E, F, W, I, S` with no ignores, and the diff adds no suppressions.

I read `references/injection.md`, the only reference the triage table matches for this change.

**Checklist, item by item:**
- **Verify loop and the three tool runs:** confirmed clear. All three passed, as listed above.
- **Suppressions:** confirmed clear.
- **`find_user` (`store.py:10`):** confirmed clear. `name` is now bound through a `?` placeholder, and `BASE_QUERY` is a constant.
- **Fix covers the class of issue, not only the flagged line:** unresolved. `src/userstore/store.py:15` still reads `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`.
  - `sort` comes from the request. `handler.py:12` passes `params.get("sort", "name")` straight into `list_users`.
  - This is string-built SQL fed by untrusted input, which the checklist forbids. `injection.md` also says to never build queries with f-strings on untrusted input.
  - Ruff's `S608` did not flag it, which is the data-flow gap `injection.md` warns about, so the clean lint run is not evidence it is safe.
  - A placeholder cannot bind a column name. The fix needs an allowlist of sortable columns, for example `{"id", "name"}`. It should reject any other value and build the `ORDER BY` clause from the allowlisted value.
  - The report named "user input reaches SQL in the store module", which covers the whole module, so fixing only `find_user` falls short.
- **Boundary validation of untrusted input:** unresolved, for the same reason. `sort` is never validated at `handler.py` or in the store.
- **Other checklist items:** not applicable. The diff has no SSRF, secrets, crypto, auth or dependency changes, and I found no user or system information in it.

**Next action:** run a fresh reviewer pass on `list_users` and the `sort` parameter. Add an allowlist for `sort` and a test that a malicious `sort` value is rejected.

VERDICT: UNRESOLVED
