All four action references are now SHA-pinned with version comments, and lint/test pass.

**Files changed:**
- `.github/dependabot.yml` (new) — weekly `github-actions` ecosystem check, all updates grouped into one PR
- `.github/workflows/ci.yml` — `actions/checkout` and `astral-sh/setup-uv` pinned to commit SHA with version comments
- `.github/workflows/codeql.yml` — `actions/checkout` and `github/codeql-action/{init,analyze}` pinned to commit SHA with version comments
- `README.md` — explains the SHA-pin + Dependabot grouped-PR workflow

Verification: `make lint`, `make test`, and YAML parsing of all three modified/added workflow files all passed.

Note on verification: I resolved the SHAs via `git ls-remote` against the real GitHub repos at the time of this run (2026-09-13), so they're current as of now but will go stale — that's expected, since Dependabot's job going forward is to open the PR that bumps them.

Not committed, per your instructions — let me know if you want that done.
