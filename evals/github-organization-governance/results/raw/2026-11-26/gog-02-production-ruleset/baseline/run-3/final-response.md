Pull request review is now required on the default branch for four repositories, but **`billing-api` and `ledger` may be production and are not covered**.

**What I did**
- I created the organization ruleset `production-pr-review` (id 1001). It is active, requires 1 approving review on the default branch, and has no bypass actors.
- It applies to any repository with the custom property `tier=production`. Today that is `ingest`, `web`, `infra` and `auth-service`.
- I saved the body to `rulesets/production-pr-review.json`. It is not committed.

**Decision for you: `billing-api` and `ledger`**

Both have the `production` topic (plus `payments` and `finance` respectively) but no `tier` value, so the ruleset skips them. I didn't set the property myself, because that reclassifies a repository and may affect more than this rule. If they are production, which their topics suggest, this adds them to the ruleset:

```bash
gh api -X PATCH orgs/northwind/properties/values --input - <<'EOF'
{"repository_names": ["billing-api", "ledger"],
 "properties": [{"property_name": "tier", "value": "production"}]}
EOF
```

Until then, your request for *every* production repository is only partly met.

**What I verified**
- Reading the ruleset back shows it is active with the settings above.
- I could not confirm that it takes effect on each repository. The effective-rules lookup returned 404 for every repository I checked, so the list of covered repositories comes from the property values.
- Per-repository rulesets and classic branch protection also returned 404, so I don't know what protection already existed. There were no organization rulesets before this one.

**Settings you might change**
- **Review strictness:** approvals stay valid after new commits, code owner review isn't required, and someone other than the last pusher doesn't have to approve. Tell me if you want any of these tightened.
- **Automation:** with no bypass actors, any bot or release job that pushes directly to a default branch in these repositories will now be rejected.
- **New repositories:** `tier` is optional, so a new production repository left without it won't be covered. Making the property required would help close that gap.
