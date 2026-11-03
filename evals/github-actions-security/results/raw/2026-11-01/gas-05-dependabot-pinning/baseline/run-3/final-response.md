I added a Dependabot config for the GitHub Actions your workflows use, and pinned every action reference to a commit SHA so Dependabot can maintain them. I haven't committed anything. I didn't run the workflows, and I haven't seen Dependabot open a pull request yet.

- **Dependabot:** `.github/dependabot.yml` checks the `github-actions` ecosystem weekly. A group matching `*` puts all action updates into one pull request.
- **Action references:** all six `uses:` lines in `ci.yml` and `codeql.yml` now point at a full commit SHA with the old tag as a trailing comment, for example `actions/checkout@<sha> # v5`. Dependabot updates both the SHA and the comment.
- **Resolving the pins:** I looked up each SHA with `gh api`. For `setup-uv` and `codeql-action`, the tag pointed at a tag object rather than a commit, so I followed it to the underlying commit. The pins are the current `v5`, `v6` and `v3` commits, so behaviour shouldn't change.
- **README:** it now has an "Action updates" section. It says actions are pinned to SHAs, that Dependabot opens one weekly grouped pull request, and that new actions should be added pinned with a version comment.
