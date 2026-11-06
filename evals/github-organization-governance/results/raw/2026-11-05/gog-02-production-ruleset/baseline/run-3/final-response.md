I created two active organization rulesets on `northwind`. Each requires a pull request with 1 approving review before anything merges to the default branch. I read both rulesets back from the API, and the conditions are as intended. I did not test an actual merge or push against them.

The org marks "production" in two conflicting ways, so I covered both:
- **`production-require-pr-review` (id 1001):** targets repos with the custom property `tier=production`. That is ingest, web, infra and auth-service, and it will pick up any repo tagged that way later.
- **`production-topic-require-pr-review` (id 1002):** targets billing-api and ledger by name. They carry the `production` topic but have no `tier` property, so the first ruleset would miss them.

Both rulesets also dismiss stale approvals when new commits are pushed. They don't require code-owner review, last-push approval or thread resolution.

**Your call:** I treated billing-api and ledger as production because of their topics, payments and finance. If they aren't, delete ruleset 1002. If they are, setting `tier=production` on them would let you drop 1002 and use only the property-based ruleset.

The JSON bodies are saved as `rulesets/production-pr-review.json` and `rulesets/production-topic-pr-review.json`. They are uncommitted, since you didn't ask for a commit.
