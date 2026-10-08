Not all items are clear: the SQL injection is still present in `list_users`.

**Tooling (re-run from this context)**
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed.
- `uv run ty check` passed.
- The ruff config selects `E, F, W, I, S`. I found no repository-wide `S` disabling and no `noqa` or ignore suppressions.

These passes don't show the module is safe. `S608` can't see through the `BASE_QUERY` indirection, which `references/injection.md` warns about.

**Unresolved**
- **Residual injection in `src/userstore/store.py:15`.**
  - `list_users` still runs ``conn.execute(f"{BASE_QUERY} ORDER BY {sort}")``. `sort` is a caller-supplied string put straight into the SQL.
  - Placeholders can't bind an identifier, so this needs an allowlist of column names, rejecting anything else. A value like `name; DROP TABLE users` or a subquery would pass through as it is now.
  - This breaks the checklist item "No untrusted data reaches … string-built SQL". It also breaks `injection.md`: "Never build queries with f-strings … on untrusted input".
- **The fixer's claim is false.** The summary said "no user input is interpolated into SQL anywhere in the module". `list_users` contradicts that. The fix covered only the one flagged line, not the class of issue (SQL built from caller-supplied strings) the request named.
- **Input handling is incomplete.** The checklist item on validating untrusted input at the boundary isn't satisfied for `sort`, because there is no allowlist.

**Confirmed clear**
- `find_user` (line 10) is correctly parameterized with `?` and `(name,)`. `BASE_QUERY` is a constant.
- The ruff, format and ty checks are clean.
- The `S` suppression check is clear.

I didn't check the dependency, SSRF, secrets, crypto or access-control items, because the diff doesn't touch them.

**Next action:** a fresh reviewer pass on `list_users`. It should add an allowlist for `sort`, for example a frozenset of permitted columns with a `ValueError` otherwise, and then re-run ruff and ty.

VERDICT: UNRESOLVED
