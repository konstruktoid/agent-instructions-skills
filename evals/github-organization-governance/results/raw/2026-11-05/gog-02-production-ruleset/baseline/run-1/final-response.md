I created an active organization ruleset, `production-default-branch-pr-review` (id 1001), that requires pull request review on the default branch of repos with `tier=production`. It currently covers four repos, not the six that look like production.

The ruleset requires 1 approving review before merging and dismisses stale approvals when new commits are pushed. I checked the API response, which echoes back the rule targets and `active` enforcement. I haven't tested an actual merge. The body is saved at `rulesets/production-default-branch-pr-review.json`, and I haven't committed it.

- **Covered:** `ingest`, `web`, `infra` and `auth-service` have `tier=production`, which the org's property schema defines as the classification field.
- **Not covered:** `billing-api` (topics `production,payments`) and `ledger` (topics `production,finance`) have the `production` topic but no `tier` value. They look like production, and the payments and finance repos are the ones you'd most want protected, but I didn't want to guess which signal you meant.

To cover them, set `tier=production` on both repos. The ruleset will pick them up automatically.

I can set that property if you want. I haven't changed anything on those repos.
