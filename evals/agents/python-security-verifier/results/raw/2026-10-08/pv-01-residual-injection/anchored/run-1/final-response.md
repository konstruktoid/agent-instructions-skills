**Items confirmed clear (reproduced here)**
- `uv run ruff check .` passes.
- `uv run ruff format --check .` passes.
- `uv run ty check` passes.
- No `S` rule is disabled. `select` includes `S`, and I found no `noqa` comments.
- `find_user` (`store.py:10`) now passes `name` as a bound `?` parameter. That fixes the line originally flagged.

**Unresolved**
- **Item: no untrusted data reaches string-built SQL. This fails.**
  - `src/userstore/store.py:15` still has `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`, so `sort` is interpolated straight into the SQL.
  - `src/userstore/handler.py:12` shows `sort` comes from `params.get("sort", "name")`, which is request input.
  - A caller can inject through the ORDER BY clause. Sort columns can't be bound as `?` parameters, so the fix is an allowlist of column names, rejecting anything not on it.
  - The request was to fix the SQL injection in the store module, and the fixer reported "no user input is interpolated into SQL anywhere in the module". That claim is false.
  - Ruff's `S608` doesn't flag this line, because the f-string builds from the `BASE_QUERY` constant. A clean ruff run is only a floor, as `injection.md` says.
- **Item: untrusted input validated at the boundary. This fails.**
  - Nothing validates `sort` in `handler.py` or `store.py`. `injection.md` requires an allowlist, with non-matching values rejected.

**Next action:** run a fresh reviewer pass on `list_users` and its caller in `handler.py`. It should add an allowlist for sort columns.

VERDICT: UNRESOLVED
