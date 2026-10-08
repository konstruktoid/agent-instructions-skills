I added Dependabot for GitHub Actions and pinned every action in the workflows to a commit SHA. I haven't committed anything, and I haven't run the workflows with the new pins.

- **Dependabot:** `.github/dependabot.yml` checks the `github-actions` ecosystem weekly. A group with the pattern `*` puts all updates into one pull request.
- **Pinning:** Dependabot can update SHA pins and keeps the trailing version comment in step with them, so I replaced the major-version tags (`@v5`, `@v6`, `@v3`) with SHAs. Each pin has a version comment, and I took the SHAs from the upstream repositories. Because the old tags floated, the pins land on newer releases than before:
  - `actions/checkout` → `fbc6f39…` (v5.1.0)
  - `astral-sh/setup-uv` → `d0cc045…` (v6.8)
  - `github/codeql-action/init` and `github/codeql-action/analyze` → `1190a97…` (v3.38.2)
- **README:** I replaced the old line saying there was no Dependabot configuration. The new "Action updates" section explains the SHA pinning and the weekly grouped pull request. It also says to pin any new action to a SHA with a version comment.
