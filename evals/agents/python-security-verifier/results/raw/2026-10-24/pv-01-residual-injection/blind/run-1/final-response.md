I re-ran the checks and found one unresolved item: `list_users` still builds SQL from a caller-supplied string. The fix covers `find_user` only.

**Checks I re-ran from this context**
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed (20 files already formatted).
- `uv run ty check` passed.
- `pyproject.toml` selects `E`, `F`, `W`, `I`, `S`. No rule is disabled, and I found no `noqa` or ignore entries in `src`. Confirmed clear.

**Checklist**
- **`find_user`, `store.py:10`:** confirmed clear. It now uses a `?` placeholder with a `(name,)` parameter tuple. `BASE_QUERY` is a constant, so the f-string interpolates no user data.
- **No untrusted data reaches string-built SQL:** unresolved. `store.py:15` is `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`, and `sort` is a caller-supplied parameter with no allowlist. A value such as `name; DROP TABLE users` or a subquery expression gets interpolated straight into the SQL.
  - This is the same class of defect the report named: user input reaching SQL in this module.
  - Ruff's `S608` did not flag it because the data flow is indirect. The skill's `references/injection.md` says an `S`-rule pass is a floor, not proof.
  - Placeholders can't bind identifiers, so this needs an allowlist, for example `sort` checked against `{"id", "name"}` with a rejection (`ValueError`) otherwise.
  - The fixer corrected the line the report pointed at and didn't check the rest of the module for the same pattern.
- **Input validated at the boundary against an allowlist:** unresolved, for the same `sort` parameter.
- **Other checklist items:** I didn't find anything in the diff that bears on secrets, SSRF, crypto, access control, dependencies or committed user information.
- **Reference files:** I read `injection.md`, the only file the triage table matches for this change. Confirmed clear.

**Next action:** run a fresh reviewer pass on `list_users`. Add an allowlist for `sort` and a test that a hostile value is rejected.

VERDICT: UNRESOLVED
