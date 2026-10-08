Dependabot is now set up to update the workflow actions weekly in one grouped pull request, and the action references are pinned so it can maintain them. I haven't run the workflows or Dependabot, so the pins and config are untested.

- **Dependabot config:** the new `.github/dependabot.yml` covers the `github-actions` ecosystem with a weekly schedule. A `*` group puts all action updates into a single PR.
- **Pinned actions:** I replaced the major-version tags in `ci.yml` and `codeql.yml` with full commit SHAs, each followed by a version comment. Dependabot rewrites both the SHA and the comment when it bumps an action. I took each SHA from the upstream tag that the old major tag pointed to today:
  - `actions/checkout` is at v5.1.0.
  - `astral-sh/setup-uv` is at v6.8.0.
  - `github/codeql-action` (`init` and `analyze`) is at v3.38.2.
- **README:** a new "Action updates" section explains the pinning, the weekly grouped PR, and that new actions should be added pinned to a SHA with a version comment. I removed the old line saying there was no Dependabot configuration.

I haven't committed anything.
