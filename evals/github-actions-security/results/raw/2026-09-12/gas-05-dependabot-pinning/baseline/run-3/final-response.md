No `actionlint` binary available, but all three YAML files parse cleanly and the changes are self-consistent. Summary of changes:

- **`.github/dependabot.yml`** (new) — weekly `github-actions` ecosystem updates, grouped into a single PR via a wildcard group.
- **`.github/workflows/ci.yml`**, **`.github/workflows/codeql.yml`** — action refs changed from mutable major-version tags (`@v5`, `@v6`, `@v3`) to full commit SHAs with a version comment, matching what Dependabot will maintain going forward.
- **`README.md`** — documents the SHA-pinning + weekly grouped-PR process.

I did not commit anything, per your instructions. Let me know if you'd like a commit.
