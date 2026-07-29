Everything is in place and validates cleanly. Summary of changes:

- **`.github/dependabot.yml`** (new): `github-actions` ecosystem, weekly schedule, all updates grouped into a single PR via a `github-actions` group matching `*`.
- **`.github/workflows/ci.yml`** and **`.github/workflows/codeql.yml`**: action references changed from mutable major-version tags (`@v5`, `@v6`, `@v3`) to full-length commit SHAs with a version comment (e.g. `actions/checkout@fbc6f39...# v5.1.0`) — resolved via `git ls-remote` against the upstream repos. This matches how Dependabot maintains SHA-pinned actions: it bumps the SHA and updates the trailing version comment.
- **`README.md`**: explains the SHA-pinning rationale and that Dependabot opens one weekly grouped PR to bump the pins going forward.
