Everything's in place and validated:

- **`.github/dependabot.yml`** (new) — `github-actions` ecosystem, weekly schedule, all updates grouped into a single PR via `groups.github-actions.patterns: ["*"]`.
- **Workflows** (`ci.yml`, `codeql.yml`) — all `uses:` references switched from mutable major-version tags (`@v5`, `@v6`, `@v3`) to full commit SHAs with a version comment (e.g. `actions/checkout@fbc6f39... # v5.1.0`), which is the format Dependabot recognizes and will keep updated (bumping both the SHA and the comment).
- **`README.md`** — new section explaining the SHA-pinning convention, why it's used, and that Dependabot handles weekly bumps as one grouped PR.

SHAs were resolved live from each upstream repo's git refs (dereferencing annotated tags to their actual commits), and all three YAML files were parsed successfully with `yaml.safe_load` to confirm syntax validity.
