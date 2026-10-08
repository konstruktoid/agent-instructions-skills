**Verification report for the SQL injection fix in `src/userstore/store.py`**

The fix closes one injection point but leaves a second one in the same module, so the change is not clear.

**Checks I ran myself**
- `uv run ruff check .` passed.
- `uv run ruff format --check .` passed (19 files already formatted).
- `uv run ty check` passed.
- `pyproject.toml` selects `E, F, W, I, S` and has no `S` ignores. No `S` rule was disabled, and the diff adds no suppressions.

**Item by item**
- **`find_user`, line 10: confirmed clear.** The `name` value now goes through a `?` placeholder with a `(name,)` tuple. `BASE_QUERY` is a constant, so the f-string only interpolates a trusted literal.
- **`list_users`, line 15: unresolved.** The line is `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`, and `sort` is a caller-supplied `str` interpolated straight into the SQL. This is the same class of problem the report named, user input reaching SQL through string building. The checklist item "No untrusted data reaches … string-built SQL" and `injection.md` ("Never build queries with f-strings … on untrusted input"; "Prefer allowlists") are not met.
  - A placeholder cannot fix this, because identifiers can't be parameterized.
  - The fix is an allowlist, for example a mapping from permitted column names (`id`, `name`) to fixed SQL fragments, rejecting anything else.
  - Ruff's `S608` did not flag it, which is the "floor, not proof" case the reference warns about.
- **Class of issue, not just the flagged line: unresolved.** The fix addressed only the one flagged line, not every place user input reaches SQL in the store module.
- **Input validated at the boundary: unresolved.** `sort` has no allowlist or validation.
- **Other checklist items: not applicable.** The change doesn't touch SSRF, secrets, passwords, authorization or dependencies. The diff adds no user or system information.

**Next action:** a fresh reviewer pass to fix `list_users` with an allowlist for `sort`. It should also add a test that a malicious `sort` value is rejected.

VERDICT: UNRESOLVED
