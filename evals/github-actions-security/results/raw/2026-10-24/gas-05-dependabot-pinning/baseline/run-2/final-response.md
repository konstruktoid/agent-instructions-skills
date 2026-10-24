I added the Dependabot config and pinned every action reference to a commit SHA. I haven't committed anything. I didn't run the workflows, and Dependabot's first run will be the real test of the config.

- **`.github/dependabot.yml`:** it checks the `github-actions` ecosystem weekly. A single group matching all actions (`*`) produces one pull request per run.
- **Workflows:** all six `uses:` lines in `ci.yml` and `codeql.yml` now point at a full commit SHA, with the version in a trailing comment. Dependabot updates both the SHA and the comment. I looked up the SHAs through the GitHub API.
  - `actions/checkout`: v5.1.0
  - `astral-sh/setup-uv`: v6.8.0
  - `github/codeql-action` (`init` and `analyze`): v3.39.1
- **README:** the old "major version tag / no Dependabot" sentence is replaced by an "Action updates" section. It explains the SHA pinning, the weekly grouped pull request, and that new actions should be pinned the same way.

Each version comment names the release that the old major tag (`v5`, `v6`, `v3`) pointed to when I looked it up, so the pinned code is the same as before.
