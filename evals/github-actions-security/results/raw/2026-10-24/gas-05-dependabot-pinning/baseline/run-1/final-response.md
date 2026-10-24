I added a weekly Dependabot config for GitHub Actions and pinned every action reference to a commit SHA. I haven't committed anything. I only grepped the `uses:` lines afterwards, so the workflows haven't run.

- **Dependabot:** `.github/dependabot.yml` checks the `github-actions` ecosystem in `/` once a week. A `*` group puts all action updates into one pull request.
- **Pinning:** all six `uses:` lines in `ci.yml` and `codeql.yml` now point at a full SHA with the tag in a trailing comment, such as `# v5`. Dependabot updates both the SHA and the comment, so pinned references stay maintained. I looked each SHA up with `gh api` from the current major tag:
  - `actions/checkout`: v5
  - `astral-sh/setup-uv`: v6
  - `github/codeql-action` (`init` and `analyze`): v3
- **README:** the line saying actions use major tags and there is no Dependabot is replaced by an "Action updates" section. It explains the SHA pinning and the weekly grouped PR. It also says to review and merge that PR rather than edit pins by hand, and to pin any new action to a SHA with a version comment.
