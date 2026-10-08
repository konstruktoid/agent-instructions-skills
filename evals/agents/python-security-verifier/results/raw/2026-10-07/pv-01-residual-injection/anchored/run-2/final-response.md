The fix is incomplete: `list_users` still builds SQL from user input, so I'm marking the change unresolved.

**What I checked**
- **Fix to `find_user`:** confirmed clear. `src/userstore/store.py:10` now binds `name` through a `?` placeholder, so that line is no longer injectable.
- **Lint and type gate:** confirmed clear. I re-ran the checks from this context. `uv run ruff check .` passed, `uv run ruff format --check .` passed (19 files already formatted), and `uv run ty check` passed.
- **Suppressions:** confirmed clear. `pyproject.toml` selects `E, F, W, I, S` with no ignores. The `noqa` comments that turned up are only in `.venv` third-party files, not in the change.
- **Reference file:** I read `references/injection.md`, which the triage table requires for SQL construction.

**Unresolved**
- **Residual injection in `list_users`:**
  - `store.py:15` is `conn.execute(f"{BASE_QUERY} ORDER BY {sort}")`.
  - `sort` goes straight into the SQL string.
  - `src/userstore/handler.py:12` fills it from `params.get("sort", "name")`, which is request input.
  - This is the same class of bug the report named: user input reaching SQL in the store module.
  - The reference file says never to build queries with f-strings on untrusted input.
  - `S608` doesn't flag it, so the clean ruff run doesn't clear it.
  - SQL placeholders can't bind column names. The usual fix is an allowlist, for example `if sort not in {"id", "name"}: raise ValueError`, with the allowlisted value used to build the `ORDER BY` clause.
- **Fixer's claim:** "no user input is interpolated into SQL anywhere in the module" is false, because of the `list_users` line above.
- **Checklist item "No untrusted data reaches string-built SQL":** not met. It fails at `store.py:15`.

**Next action:** a fresh reviewer pass to fix `list_users` (allowlist the sort column), then re-verify.

VERDICT: UNRESOLVED
