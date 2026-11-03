Request `params["sort"]` goes straight into `ORDER BY` with no validation.

**Per-item results**

- Verify loop and tooling:
  - `ruff check`: confirmed clear. It passed on a fresh run, and the config selects `S`.
  - `ruff format --check`: confirmed clear.
  - `ty check`: confirmed clear.
  - Suppressions: confirmed clear. The diff adds none, and no `S` rule is disabled repository-wide.
- `find_user` (`store.py:10`): confirmed clear. It binds `name` as a `?` parameter. `BASE_QUERY` is a constant, so the f-string interpolates no user data.
- No untrusted data reaches string-built SQL: **unresolved**.
  - `src/userstore/store.py:15` has `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`.
  - `src/userstore/handler.py:12` passes `params.get("sort", "name")` into it, so request input reaches the `ORDER BY` clause unvalidated.
  - Values like `name; ...` or `(CASE WHEN (subquery) ...)` allow boolean-based data exfiltration. The sink is not parameterizable, so it needs an allowlist of column names, rejecting anything else.
  - `S608` doesn't flag it because the query is built from a constant plus a variable, which is the "assembled several calls away" case that `injection.md` warns about.
- Input validated at the boundary with an allowlist: **unresolved**, for the same `sort` parameter. No allowlist exists in `handler.py` or `store.py`.
- Fix addresses the class of issue, not just the flagged line: **unresolved**. The request was to "fix the SQL injection in the store module." The fixer patched only the one f-string at `find_user` and left the second injection in the same module.
- Not applicable to this change: SSRF, secrets, password hashing and randomness, authorization and debug config, dependency changes, and the user/system information check. The diff touches none of them, and the diff contains no such data.
- Reference files: confirmed clear. The triage table matched only `injection.md`, and I read it.

**Next action:** run a fresh reviewer pass on `list_users`/`sort`. It should add an allowlist of sortable columns (for example `{"id", "name"}`), reject anything else with `ValueError`, and add a test for a malicious `sort` value.

VERDICT: UNRESOLVED
