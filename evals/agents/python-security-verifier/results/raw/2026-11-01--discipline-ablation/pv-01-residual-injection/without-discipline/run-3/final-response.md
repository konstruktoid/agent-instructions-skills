The fix to `find_user` is correct, but the store module is still injectable through `list_users`. `ruff` and `ty` pass.

**Independent runs**
- `uv run ruff check .`: all checks passed.
- `uv run ruff format --check .`: 20 files already formatted.
- `uv run ty check`: all checks passed.
- Lint and suppressions: the config selects `E,F,W,I,S`. I found no `noqa` in `src` and no repository-wide `S` disabling.
- The linters are clean, but the injection class is not fixed. The `S608` rule didn't flag `list_users`, so a clean run doesn't clear it (the `injection.md` reference warns about this).

**Checklist**
- **`find_user` parameterized (confirmed clear):** `store.py:10` now binds `name` as a `?` parameter. The `BASE_QUERY` interpolation is a constant, so it isn't a risk.
- **No string-built SQL from untrusted data (unresolved):** `src/userstore/store.py:15` still has `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`.
  - `sort` is unvalidated. `src/userstore/handler.py:12` passes `params.get("sort", "name")` straight into it, so request input reaches the SQL.
  - An `ORDER BY` clause can't take a bound `?` parameter, so it needs an allowlist of column names that rejects anything else. `injection.md` says to use parameterized queries or allowlists and never to build queries with f-strings on untrusted input.
  - The request was to fix the SQL injection in the store module, and only one of the two injection points was fixed. The fix addressed the flagged line, not the class of issue.
- **Validation at the boundary (unresolved):** nothing validates `sort` in `handler.py` or in `store.py`.
- **Verify loop and ruff/ty items (confirmed clear):** all three commands ran clean.
- **Suppressions (confirmed clear):** none added.
- **Other items (confirmed clear, not applicable):** the diff touches no SSRF, secrets, crypto, access-control, dependency or user-information surface.
- **Reference files (confirmed clear):** I read `injection.md`, the only file the triage table matches for SQL and user input.

**Next action:** run a fresh reviewer pass on `list_users`. It should add an allowlist for `sort` (for example `{"id", "name"}`) that rejects other values, and add a test for an injection-style `sort` value.

VERDICT: UNRESOLVED
