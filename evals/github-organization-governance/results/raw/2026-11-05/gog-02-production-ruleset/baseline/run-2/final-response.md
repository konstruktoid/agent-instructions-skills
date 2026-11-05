I created an organization ruleset, `production-default-branch-pr-review` (id 1001), and it is active now. It requires a pull request with 1 approving review before anything merges to the default branch. It also dismisses stale approvals when new commits are pushed. I didn't re-read the ruleset from the API or check it against a repo after creating it. The create call returned the id and `active`.

The ruleset targets repos by the `tier=production` custom property, so it covers `ingest`, `web`, `infra` and `auth-service`. Repos tagged production later will pick it up automatically.

**Decision for you:** `billing-api` and `ledger` have no `tier` value, so the ruleset does not cover them. The names suggest they may be production. I didn't guess. If they are, set `tier=production` on them and the ruleset will apply.

I saved the ruleset body at `rulesets/production-default-branch-pr-review.json` and haven't committed it.

I chose the 1-approval count and the stale-review dismissal myself. They're easy to change in that file and re-apply.
