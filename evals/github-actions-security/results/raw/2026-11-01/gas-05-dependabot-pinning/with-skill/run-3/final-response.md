I added `.github/dependabot.yml` and pinned every action reference to a commit SHA. `actionlint` is clean. `zizmor --persona=pedantic` reports 3 low-severity findings (listed below) that I left alone.

**Dependabot.** The config checks the `github-actions` ecosystem weekly and groups all action updates into one pull request. It has a 7-day cooldown, so a brand-new release isn't adopted until it has been out a week.

**Pinning.** Dependabot can rewrite SHA pins and their version comments, so I pinned each action to a full SHA with a `# vX.Y.Z` comment. I looked up the releases and SHAs with `gh`. The jumps are all major versions, but none of the changes I checked in the release notes affect these workflows. They run on `pull_request`, `push` and `schedule`, not `pull_request_target`, `workflow_run` or `release`, and they use GitHub-hosted runners.

| Action | Before | Now |
|---|---|---|
| `actions/checkout` | `v5` | v7.0.1 |
| `astral-sh/setup-uv` | `v6` | v10.3.2 |
| `github/codeql-action` (`init` and `analyze`) | `v3` | v4.39.1 |

- **`setup-uv` is one release behind.** v10.3.3 is the newest, but it was published 4 days ago, inside the cooldown, so I chose v10.3.2.
- **`codeql-action` needed its tags.** The "latest release" API returned a CodeQL bundle marker rather than an action release, so I took v4.39.1 from the tags and releases list.

**README.** It now explains that actions are SHA-pinned and that Dependabot updates them weekly in one grouped pull request with the cooldown. It also tells reviewers to read the upstream diff between the old and new SHA before merging, and not to edit pins by hand.

**`zizmor` findings.** All 3 are low-severity pedantic findings that were already there:
- Both workflows are missing a concurrency setting.
- `security-events: write` in `codeql.yml` has no explanatory comment.

I didn't run the workflows on a runner, so nothing has been run live. I made no commit or push.
