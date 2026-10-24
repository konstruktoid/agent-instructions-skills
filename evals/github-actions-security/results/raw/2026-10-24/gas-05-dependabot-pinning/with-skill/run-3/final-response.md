Dependabot is now set up for the workflows' actions, and every `uses:` line is pinned to a commit SHA. `actionlint` is clean. `zizmor` in pedantic mode reports 3 low findings, listed below. I didn't run the workflows because that needs a push, so the changes are unverified on a runner. I haven't committed anything.

**Dependabot config:** `.github/dependabot.yml` checks the `github-actions` ecosystem weekly. It puts all action updates into one grouped pull request. I added a 7-day cooldown, so a brand-new release isn't proposed straight away.

**Pins:** each reference now has the version in a trailing comment, and I looked up each SHA with `gh api`. I picked the newest release that was at least 7 days old today (2026-10-24):

| Action | Was | Now | Notes |
|---|---|---|---|
| `actions/checkout` | `@v5` | v7.0.1 | Newest release, published 2026-07-20. |
| `astral-sh/setup-uv` | `@v6` | v10.3.0 | v10.3.1 and v10.3.2 came out 2026-10-21 and 2026-10-22, so the cooldown held them back. |
| `github/codeql-action/init` and `/analyze` | `@v3` | v4.39.0 | v4.39.1 came out 2026-10-21, so the cooldown held it back. v3 is a maintenance line. |

Three of these are major-version jumps (checkout 5→7, setup-uv 6→10, codeql-action 3→4), so I read the release notes for the two newest majors.
- **setup-uv v10:** it turns off the cache by default for `pull_request_target`, `workflow_run` and `release` events. This repo uses none of those, so nothing changes here.
- **codeql-action v4.39.0:** it raises the minimum CodeQL bundle version to 2.20.7.
- **Not checked:** I didn't read the notes for every intermediate release.

**README:** it now has a "How action updates are handled" section. It covers the SHA pins, the weekly grouped pull request, the cooldown, and how to review those pull requests. It tells reviewers to read the upstream diff between the old and new SHAs and to merge the pull requests promptly. It also says not to edit action versions by hand.

**Remaining `zizmor` findings:** all three are low-severity and were already in the repo.
- Neither workflow sets `concurrency`.
- `security-events: write` in `codeql.yml` has no explanatory comment.

I left them alone because they're outside what you asked for. I can fix them if you want.
