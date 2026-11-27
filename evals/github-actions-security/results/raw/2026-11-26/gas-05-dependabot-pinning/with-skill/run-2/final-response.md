I added `.github/dependabot.yml`, replaced all the tag references in both workflows with commit SHAs, and added an "Action updates" section to the README. Nothing is committed, and the workflows haven't run.

**Dependabot:** it checks `github-actions` weekly and groups all version updates into one pull request. I also added a 7-day cooldown, which you didn't ask for, so a release isn't proposed until it's a week old. Security updates skip both the cooldown and this grouping.

**Pins:** each is a full commit SHA with the version in a comment, which Dependabot updates along with the SHA. I matched each SHA to its release tag.

| Action | Before | Now | Newer releases held back by the cooldown |
|---|---|---|---|
| `actions/checkout` | `v5` | `v7.0.1` | none |
| `astral-sh/setup-uv` | `v6` | `v10.3.3` | `v10.4.0` |
| `github/codeql-action` (`init`, `analyze`) | `v3` | `v4.39.3` | `v4.39.4`, `v4.39.5` |

**Major upgrades to note in the pull request description**
- **All three:** the pinned versions run on Node 24. This is fine on `ubuntu-latest`.
- **`actions/checkout`:** `v7` blocks checking out fork pull requests under `pull_request_target` and `workflow_run`. Neither workflow uses those triggers.
- **`setup-uv`:**
  - `v7` and `v8` remove an input and an old manifest format, neither of which you use.
  - `v9` stops pruning the cache by default, so cache usage may grow.
  - `v10` disables caching on some triggers you don't use.
- **`codeql-action`:** recent `v4` releases raise the minimum CodeQL bundle version. You don't set one, so this shouldn't affect you.

I read the major-version release notes for `checkout` and `setup-uv`, but only part of the CodeQL changelog, and not every release in between.

**Checks**
- **`actionlint`:** passes.
- **`zizmor` (pedantic, offline):** reports 3 low-severity findings, so it isn't clean. Two are missing `concurrency` settings (one per workflow) and one is an uncommented `security-events: write` in `codeql.yml`. These lines predate this change, so I left them; I can fix them if you like.
- **Not checked:** `zizmor`'s online audits didn't run. `gh` isn't authenticated and the GitHub API was rate-limited, so I got versions and SHAs from public release pages and `git ls-remote`.

**Still to verify**
- **CI:** opening a pull request will exercise the new `checkout` and `setup-uv` pins.
- **CodeQL:** `codeql.yml` only runs on its schedule (Mondays, 03:00 UTC), so a pull request won't test it. Check the first scheduled run after merging. The README says to do the same for later CodeQL updates.

`setup-uv` still installs the latest `uv` at run time because no `version` input is set. Pinning the action doesn't fix that, and Dependabot's actions updates won't manage it.
