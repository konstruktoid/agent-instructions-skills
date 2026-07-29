All changes look correct. Summary:

- **`.github/dependabot.yml`** (new): checks the `github-actions` ecosystem weekly and groups all updates into a single PR via a wildcard group.
- **`.github/workflows/ci.yml`** and **`codeql.yml`**: action references switched from mutable tags (`@v5`, `@v6`, `@v3`) to full commit SHAs with a trailing version comment (e.g. `actions/checkout@fbc6f399... # v5.1.0`), which is the format Dependabot updates in place — matching how it will maintain them going forward.
- **`README.md`**: new section explaining that actions are pinned by SHA for security and that Dependabot opens one weekly PR bundling any available updates.

Verified all three YAML files parse correctly with `yaml.safe_load`, and confirmed each pinned SHA against the actual tag on GitHub via `git ls-remote` (dereferencing annotated tags where needed).
