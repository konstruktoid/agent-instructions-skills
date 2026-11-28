I added `.github/dependabot.yml`, pinned all the action references to commit SHAs and explained the process in the README. Nothing is committed or pushed, and no workflow has run with the new versions.

**Dependabot:** it checks GitHub Actions weekly and groups all version updates, including major ones, into one pull request. I also added a 7-day cooldown, which you didn't ask for, so brand-new releases aren't proposed immediately.

**Action references:** each is now a full SHA with the version in a comment, which Dependabot updates together. This also upgrades every action by at least one major version:

| Action | Before | After | What changes |
|---|---|---|---|
| `actions/checkout` | `v5` | `v7.0.1` | v7 blocks checking out fork pull requests under `pull_request_target` and `workflow_run`; you use neither trigger. |
| `astral-sh/setup-uv` | `v6` | `v10.4.0` | Runs on Node 24, no longer prunes the cache by default (cache use may grow), and turns caching off for some sensitive events that you don't use. |
| `github/codeql-action` | `v3` | `v4.39.4` | Runs on Node 24. `v4.39.5` exists but is only 4 days old, so the cooldown holds it back. |

I checked the release notes at the major-version boundaries, mostly the opening part of each, not every release in between.

**Checks:**
- The SHAs were looked up from each action's release tag.
- `actionlint` passes.
- `zizmor` (pedantic, offline) is not clean: it reports 3 low-severity findings. Two are missing `concurrency` settings in both workflows, and one is an uncommented `security-events: write` in `codeql.yml`. They are outside this change, so I left them.
- Running offline skipped `zizmor`'s checks that need the GitHub API, including known-vulnerability lookups.

**After you push:**
- **CI:** open a pull request and check that `Test` passes, including the cleanup step after `setup-uv`. `make test` only echoes a message and never calls uv, so watch for cache warnings or errors there.
- **CodeQL:** it only runs on Mondays and has no manual trigger, so the pull request won't test it. Check the first scheduled run after merging, or add `workflow_dispatch` if you want to run it on demand.
- **Security alerts:** Dependabot doesn't raise them for SHA-pinned actions, so merge the weekly pull requests promptly.
- **uv version:** pinning `setup-uv` doesn't pin uv itself. With no version configured, it still installs the latest uv, and Dependabot's actions updates won't manage that.
