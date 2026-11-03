The fixer fixed `find_user` but left a second SQL injection in the same module, so I'm marking this unresolved.

**Checks I re-ran from this context**
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed (20 files already formatted).
- `uv run ty check` passed.
- The ruff config selects `E, F, W, I, S`. No `S` rule is disabled repository-wide, and the diff adds no suppressions.

**Checklist items**
- **`find_user` (`store.py:10`): confirmed clear.** It now uses a `?` placeholder with `(name,)`, so `name` is bound as a value and never becomes SQL text.
- **Lint and type gate: confirmed clear.** All three commands pass and no suppressions were added.
- **No untrusted data reaches string-built SQL: unresolved.** `list_users` at `src/userstore/store.py:15` is `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`. `sort` is a caller-supplied `str` interpolated straight into the statement. A value such as `name; DROP TABLE users` or `(SELECT ...)` is injectable. Parameter binding can't fix this, because identifiers can't be bound. The fix is to check `sort` against an allowlist such as `{"id", "name"}` and reject anything else, then interpolate only the allowlisted value. `references/injection.md` requires this, and says input validation and sink handling are separate controls.
- **Class of issue, not just the flagged line: unresolved.** The request said to fix the SQL injection in the store module. The fix addressed only the one line that was flagged.
- **Why ruff is clean anyway.** `S608` doesn't flag `list_users` because the query goes through the `BASE_QUERY` constant. The passing lint run is therefore not evidence that the module is safe. The skill says to treat an `S` pass as a floor.
- **Other checklist items (SSRF, secrets, crypto, auth, dependencies): not applicable.** The diff doesn't touch them.

**Next action:** run a fresh reviewer pass on `list_users`. It should add an allowlist for `sort` and a test that a malicious `sort` value is rejected.

VERDICT: UNRESOLVED
