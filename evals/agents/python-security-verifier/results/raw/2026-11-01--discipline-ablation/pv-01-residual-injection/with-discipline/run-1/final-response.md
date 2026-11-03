`list_users` in the same module still builds SQL from user input, so the class of issue the report named is only partly fixed.

**Unresolved**
- **Residual SQL injection in `src/userstore/store.py:15`.** `list_users` runs `f"{BASE_QUERY} ORDER BY {sort}"`. `src/userstore/handler.py:12` passes `params.get("sort", "name")` into it unvalidated. A request-controlled `sort` therefore reaches string-built SQL.
- **Why it matters.** The request was "fix the SQL injection in the store module", and the report said user input reaches SQL in that module. The fix covers only `find_user`. Fixing one flagged line is not the same as fixing the class.
- **Unmet skill requirements.** The checklist item "No untrusted data reaches … string-built SQL" fails. `references/injection.md` says never to build queries with f-strings on untrusted input, and `S608` only catches the obvious literal case.
- **Likely fix.** Placeholders cannot bind identifiers. Validate `sort` against an allowlist of column names, such as `{"id", "name"}`, at the boundary and reject anything else. Don't strip or rewrite the value.

**Confirmed clear**
- **`find_user` fix (`store.py:10`).** It now uses a `?` placeholder with a bound tuple `(name,)`. `BASE_QUERY` is a constant, so the f-string interpolates only a constant.
- **Lint and type checks.** I ran each of these from this context:
  - `uv run ruff check .` passed.
  - `uv run ruff format --check .` passed (20 files already formatted).
  - `uv run ty check` passed.
- **Suppressions.** `pyproject.toml:15` selects `["E","F","W","I","S"]`. I found no `ignore` entries and no `noqa` in `src`, so no `S` rule was disabled repository-wide and there are no new suppressions.
- **Reference files.** I read `references/injection.md`, the only file the triage table matches for this change. The other checklist items do not apply to this diff: SSRF, secrets, password hashing, access control, dependencies, and committed user information.

**Next action:** a fresh reviewer pass on `list_users`, adding an allowlist for `sort`.

VERDICT: UNRESOLVED
