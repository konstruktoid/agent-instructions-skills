**Verification of the SQL injection fix in `src/userstore/store.py`**

The fix closes only the `find_user` injection. The same class of bug is still open in `list_users`, so the change is not clear.

**Unresolved**
- **Residual SQL injection, `store.py:15`.** `list_users` still runs `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`. `src/userstore/handler.py:12` fills `sort` from `params.get("sort", "name")`, which is request input. A value such as `name; ...` or a subquery in the sort position reaches SQL unchecked. The fixer's claim that "no user input is interpolated into SQL anywhere in the module" is false.
- **Skill requirements not met.** `references/injection.md` says never to build queries with f-strings on untrusted input. The checklist item "no untrusted data reaches … string-built SQL" fails.
- **Why `ruff` missed it.** `S608` did not flag it, which is the "floor, not proof" case the skill warns about.
- **What the fix should do.** A column name cannot be a bound parameter. The sort value should be checked against an allowlist of column names, for example `{"id", "name"}`, and rejected if it is not on the list. That check belongs at the boundary or just before the query is built.

**Confirmed clear**
- **`find_user`, `store.py:10`.** It now uses a `?` placeholder with `(name,)`. This is correct and parameterized.
- **`ruff check .`.** I re-ran it and it passed. `select = ["E","F","W","I","S"]` is unchanged and I found no suppressions.
- **`ruff format --check .`.** I re-ran it and it passed (19 files already formatted).
- **`ty check`.** I re-ran it and it passed.
- **Suppressions.** There is no repository-wide `S` disabling and no `noqa` in `src` or `tests`.
- **Reference files.** I read `references/injection.md`, the only file the triage table matched.

The other checklist items (SSRF, secrets, passwords, authorization, dependencies, user or system information) don't apply to this diff.

**Next action:** run a fresh reviewer pass on `list_users` to add the allowlist for `sort`, and add a test that a hostile `sort` value is rejected.

VERDICT: UNRESOLVED
