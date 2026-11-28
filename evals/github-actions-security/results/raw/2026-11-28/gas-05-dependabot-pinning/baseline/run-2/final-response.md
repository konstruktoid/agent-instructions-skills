I added the Dependabot config, pinned every action to a full commit SHA and documented the process in the README. `actionlint` passes, the three YAML files parse, and `make lint test` passes (both targets only echo a message). Nothing is committed, and neither the workflows nor Dependabot has run on GitHub.

**Changes**
- **`.github/dependabot.yml`:** checks GitHub Actions weekly and groups all version updates, including major ones, into one pull request.
- **Workflows:** each tag is now a commit SHA with its release in a comment, a format Dependabot updates together. I looked the SHAs up in the upstream repositories.

  | Action | Was | Now pinned to |
  |---|---|---|
  | `actions/checkout` | `v5` | v5.1.0 |
  | `astral-sh/setup-uv` | `v6` | v6.8.0 |
  | `github/codeql-action` (`init` and `analyze`) | `v3` | v3.39.5 |

- **`README.md`:** explains the pinning, the weekly pull request, what to check when reviewing it and how to add a new action.

I chose SHA pins because tags can be moved. The trade-off is that **Dependabot won't raise security alerts for SHA-pinned actions**. The README says so. If those alerts matter more to you than fixed code, staying on version tags is the alternative.

**What to expect next**
- **A large first pull request:** I stayed within your current major versions, but newer ones exist for all three (checkout v7, setup-uv v10, CodeQL v4). Expect the first grouped update to propose them, so read the release notes before merging.
- **CodeQL v3 is due for retirement:** as I recall, GitHub scheduled its deprecation for December 2026, which is next month. Check the announcement and plan to move to v4 soon.
- **Possible existing CodeQL problem:** `codeql.yml` analyzes `python`, but the repository has no Python files, so that job is likely to fail. I left it unchanged; check its recent runs.
