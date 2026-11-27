I added `.github/dependabot.yml`, pinned every action to a commit SHA with a version comment, and explained the update process in the README. `actionlint` passes, but `zizmor` still reports 3 low findings. Nothing is committed, and no workflow has run with the new versions.

**Dependabot:** it checks GitHub Actions weekly and groups all version updates, including major ones, into one pull request. I also added a 7-day cooldown, so it won't propose a release newer than that. Security update pull requests, if any are raised, aren't covered by this group.

**Pins:**

| Action | Was | Now | Newer release held back by the cooldown |
|---|---|---|---|
| `actions/checkout` | `v5` | `v7.0.1` | none |
| `astral-sh/setup-uv` | `v6` | `v10.3.3` | v10.4.0 (Nov 20) |
| `github/codeql-action` (`init`, `analyze`) | `v3` | `v4.39.3` | v4.39.4 (Nov 20), v4.39.5 (Nov 24) |

I took the SHAs from each repository's tags with `git ls-remote`. `gh` wasn't authenticated and the public API was rate-limited.

**Major version jumps**

I moved to current releases rather than pinning the old major versions, so check these in the pull request:
- **`checkout` v5 → v7:** v7 blocks checking out fork pull request code under `pull_request_target` and `workflow_run`. Your workflows use neither trigger.
- **`setup-uv` v6 → v10:**
  - The cache is no longer pruned by default, so it may use more storage.
  - Automatic caching is now off for some events, none of which you use.
  - The removed `server-url` input and old manifest format aren't used here.
- **`codeql-action` v3 → v4:** this moves to the Node 24 runtime. Your only input is `languages`. I didn't read the whole v3 to v4 changelog, only the recent v4 entries.

**Checks still open**
- **`zizmor` findings:** all three were left as they are because they concern lines this task didn't change:
  - `ci.yml` has no `concurrency` setting.
  - `codeql.yml` has no `concurrency` setting.
  - `security-events: write` in `codeql.yml` has no explanatory comment.
- **Offline audit:** `zizmor` ran offline, so its checks that need the GitHub API were skipped.
- **CI:** opening a pull request will exercise the new `checkout` and `setup-uv` versions.
- **CodeQL:** `codeql.yml` only runs on its Monday schedule, so the first run after merging is its real test. Check that one.

I can fix the three `zizmor` findings as a separate change if you like.
