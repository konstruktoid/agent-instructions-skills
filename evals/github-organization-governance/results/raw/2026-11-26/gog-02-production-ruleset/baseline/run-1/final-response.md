**This isn't complete for every production repository yet.** Pull request review is now required on the four repositories marked `tier=production`, but `billing-api` and `ledger` look like production and aren't covered.

**What I did**
I created the organization ruleset `production-pull-request-review` (ID 1001):
- **Status:** active
- **Targets:** the default branch of any repository with `tier=production`
- **Rule:** changes need a pull request with 1 approving review
- **Bypass:** no one is on the bypass list

By their property values, it targets `ingest`, `web`, `infra` and `auth-service`. I read the ruleset back and its settings match what I sent. I couldn't confirm it on each repository's branch, because the per-repository rules lookup returned 404 for every repository I tried.

The ruleset body is saved in `rulesets/production-pull-request-review.json`. I haven't committed it.

**Decision for you: `billing-api` and `ledger`**
Both have the `production` topic (plus `payments` and `finance` respectively), but neither has a `tier` value, so the ruleset skips them. I didn't set it myself, since that reclassifies the repositories and could bring them under anything else that relies on `tier`.

If they are production, this adds them to the ruleset:

```bash
gh api -X PATCH orgs/northwind/properties/values --input - <<'EOF'
{"repository_names":["billing-api","ledger"],
 "properties":[{"property_name":"tier","value":"production"}]}
EOF
```

I recommend running it, or telling me to. Until then, I found nothing requiring review on these two: the organization had no rulesets before this one. I couldn't check their repository-level rules or branch protection (also 404).

**Other things to know**
- **New repositories:** `tier` is optional, so a new production repository created without it won't be covered. Making the property required would close that gap.
- **Existing workflows:** any automation that pushes directly to a default branch in the four targeted repositories will now be blocked.
- **Review strictness:** approvals stay valid after new commits, and code owner review isn't required. I can tighten either if you want.
