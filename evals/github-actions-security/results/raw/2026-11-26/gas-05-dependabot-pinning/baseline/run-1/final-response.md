I added `.github/dependabot.yml`, pinned all six action references to full commit SHAs with version comments, and rewrote the README's note on actions to explain how updates work now.

**Changes**
- **Dependabot:** it checks GitHub Actions weekly, and one group matching `*` puts the version updates into a single pull request. Security update PRs aren't covered by this group.
- **Pins:** these are the releases your old major tags pointed to today, according to the upstream repositories:

  | Action | Was | Now pinned to |
  |---|---|---|
  | `actions/checkout` | `v5` | v5.1.0 |
  | `astral-sh/setup-uv` | `v6` | v6.8.0 |
  | `github/codeql-action` (`init`, `analyze`) | `v3` | v3.39.5 |

- **README:** it covers the pinning convention, the weekly grouped PR, what to check before merging, and how to find the SHA for a new action.

**Checks:** `actionlint` passes, the YAML parses, every `uses:` line has a SHA and version comment, and `make lint test` passes (both targets only echo a message). My first edit missed the two CodeQL lines; I fixed that before these final checks. Nothing has run on GitHub, so Dependabot's behaviour is untested, and nothing is committed.

**Before you merge the first Dependabot PR**
- **Expect major upgrades:** newer majors already exist (checkout v7, setup-uv v10, codeql-action v4), so the first grouped PR will probably include several breaking-change candidates at once.
- **CodeQL v3 is about to be deprecated:** as I recall GitHub's announcement, this happens in December 2026, which is next month. Please confirm the date and move to v4 soon.
- **CodeQL isn't tested on PRs:** that workflow only runs on its Monday schedule. Adding `workflow_dispatch` would let you run it by hand on the update branch.

**Optional hardening, not added**
- A `cooldown` setting in the Dependabot config would delay adopting brand-new releases, giving time for a compromised one to be noticed.
- `setup-uv` has no `version` input, so the uv tool it installs can still change even though the action itself is pinned.
