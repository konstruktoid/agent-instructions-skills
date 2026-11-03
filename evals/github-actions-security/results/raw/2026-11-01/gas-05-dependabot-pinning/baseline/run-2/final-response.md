I added a Dependabot config and pinned every action reference to a commit SHA. I haven't committed anything. I also haven't run the workflows or Dependabot, so none of this has been exercised.

- **`.github/dependabot.yml`**: checks the `github-actions` ecosystem weekly. A single `github-actions` group matches all actions (`*`), so each week's updates come as one pull request.
- **Workflows** (`ci.yml`, `codeql.yml`): each action now points at the commit its old major tag resolved to, with the release in a trailing comment. Dependabot updates both the SHA and the comment.

| Action | Pinned to |
|---|---|
| `actions/checkout` | `fbc6f39…` (v5.1.0) |
| `astral-sh/setup-uv` | `d0cc045…` (v6.8.0) |
| `github/codeql-action/init` and `analyze` | `4bfa242…` (v3.39.1) |

- **`README.md`**: the old "referenced by major version tag" line is gone. A new "Action updates" section explains the SHA pinning, the weekly grouped Dependabot pull request, and that new actions should be pinned the same way.

I resolved the SHAs with `gh api`, following annotated tags to the underlying commit. I picked the newest release tag on each commit as the comment, so each SHA is the commit the old tag pointed to.
