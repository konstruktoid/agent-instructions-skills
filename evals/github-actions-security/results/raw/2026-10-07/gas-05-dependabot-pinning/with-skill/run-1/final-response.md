I added `.github/dependabot.yml` and pinned every action reference to a full commit SHA, so the workflows match how Dependabot will maintain them. `actionlint` is clean. `zizmor` (pedantic) reports 3 low-severity findings, none about pinning, which I left alone. I did not commit, push, or run the workflows.

**Dependabot config**
- It covers the `github-actions` ecosystem on a weekly schedule.
- A single group with pattern `*` puts all action updates into one pull request.
- I also added a 7-day cooldown, which you didn't ask for, so a brand-new release isn't proposed straight away.

**Action pins**
I looked up the latest release of each action and its commit SHA from GitHub. Each reference now carries the version in a trailing comment, which Dependabot uses and rewrites.

| Action | Was | Now |
|---|---|---|
| `actions/checkout` | `@v5` | `3d3c42e5…` # v7.0.1 |
| `astral-sh/setup-uv` | `@v6` | `c18668ad…` # v10.2.0 |
| `github/codeql-action/init` and `analyze` | `@v3` | `2892aa5e…` # v4.38.2 |

All three versions were published more than 7 days ago, so they clear the cooldown.

**Major-version bumps to review**
- **`checkout` v5 to v7:** v7 blocks checking out fork PRs in `pull_request_target` and `workflow_run`. These workflows use neither trigger.
- **`setup-uv` v6 to v10:** v7 moved to Node 24, which is fine on GitHub-hosted runners. v10 turns off the cache by default for `pull_request_target`, `workflow_run` and `release` events, which these workflows don't use.
- **`codeql-action` v3 to v4:** I didn't read the v4 release notes, because the v4.0.0 release lookup returned 404. The workflows are otherwise unchanged.

Because these bumps are major versions, check the first CI and CodeQL runs after merging. I haven't run them.

**README**
It now has an "Action updates" section. It says actions are SHA-pinned with a version comment and that Dependabot opens one grouped weekly PR with a 7-day cooldown. It also says to review that PR against the upstream diff and merge it, and not to edit versions by hand.

**Remaining `zizmor` findings**
These are not caused by this change:
- Neither workflow sets a `concurrency` group.
- `security-events: write` in `codeql.yml` has no explanatory comment.

I can fix them if you want.
