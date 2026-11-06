I added northwind-release as a bypass actor on `default-branch-baseline`. The live ruleset (id 4401) now lists it, and I read it back to confirm.

- **Change:** the app (id 9001, type `Integration`) is in `bypass_actors` with `bypass_mode: always`.
- **Mode:** I used `always` because the app pushes version bumps straight to the default branch. `pull_request` mode only lets an actor bypass on pull requests, so it wouldn't cover direct pushes.
- **Repo file:** `rulesets/default-branch-baseline.json` has the same change. I haven't committed it.
- **Effect:** the app now skips every rule in the ruleset on production-tier repos' default branches. That covers required reviews, code-owner review, deletion protection and non-fast-forward protection. Version-bump pushes should no longer be blocked.
