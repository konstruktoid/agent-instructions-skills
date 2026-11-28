I added `.github/dependabot.yml`, pinned all six action references to full commit SHAs, and rewrote the README section on how action updates work. The YAML parses and `actionlint` reports no problems. I haven't run the workflows, and Dependabot itself can only be confirmed once this is on GitHub. Nothing is committed.

**Dependabot:** it checks GitHub Actions weekly and groups all version updates, including major ones, into one pull request. Security updates aren't part of that group.

**Pins:** each stays on the major version you were already using, at the commit its major tag points to today, according to the upstream repositories:

| Action | Before | Pinned release |
|---|---|---|
| `actions/checkout` | `v5` | v5.1.0 |
| `astral-sh/setup-uv` | `v6` | v6.8.0 |
| `github/codeql-action` (`init` and `analyze`) | `v3` | v3.39.5 |

I chose SHA pins over major tags because a tag can be moved to different code. Dependabot updates both the SHA and the version comment.

**What to expect next:**
- **A large first pull request:** newer major versions exist for these actions (for example, `checkout` v7, `setup-uv` v10 and `codeql-action` v4). Expect the first grouped update to jump majors, so read the release notes before merging.
- **CodeQL v3 deprecation:** as I recall, GitHub scheduled it for December 2026, which is next month. I didn't check that here, but it's worth confirming and moving to v4 promptly.
- **CodeQL isn't tested on pull requests:** `codeql.yml` runs only on its Monday schedule, so a green pull request says nothing about a CodeQL update. Adding a `workflow_dispatch` trigger would let you run it by hand; I didn't change any triggers.
- **uv itself:** the pin fixes the `setup-uv` action, not the version of uv it installs. If you want that fixed too, set its `version` input.
