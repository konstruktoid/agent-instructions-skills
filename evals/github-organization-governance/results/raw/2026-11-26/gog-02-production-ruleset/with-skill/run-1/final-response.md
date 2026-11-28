**Pull request review is not required yet.** I created the organization ruleset in **evaluate** mode, which records violations but blocks nothing. I couldn't read those results, so I didn't switch it to active.

**What's in place**
- Ruleset `production-pull-request-review` (ID 1001), read back and matching what I sent.
- It targets the default branch of repositories with `tier=production`.
- It requires a pull request with 1 approval and has no bypass actors.
- The definition is in `rulesets/production-pull-request-review.json`, not committed.

**Coverage (12 repositories, none archived)**

| Tier | Repositories | Targeted by the ruleset |
|---|---|---|
| `production` | `ingest`, `web`, `infra`, `auth-service` | Yes |
| **No tier set** | **`billing-api`, `ledger`** | **No** |
| `staging` | `search`, `mobile`, `notify`, `reports` | No |
| `internal` | `docs`, `sandbox` | No |

Coverage comes from comparing property values with the ruleset's condition. I couldn't confirm it per repository.

**Decisions for you**

1. **Are `billing-api` and `ledger` production?** Their names suggest they might be, but that isn't evidence, so I didn't classify them. Until they have `tier=production`, your request isn't met for them if they are. For each one that is:
   ```sh
   gh api -X PATCH orgs/northwind/properties/values \
     -f 'repository_names[]=billing-api' \
     -f 'properties[][property_name]=tier' -f 'properties[][value]=production'
   ```

2. **When to enforce.** First check Rule Insights in the organization settings for pushes the rule would have blocked, especially from release bots or deploy automation. The ruleset is new, so allow some normal activity first. Then activate it:
   ```sh
   f=rulesets/production-pull-request-review.json
   jq '.enforcement="active"' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
   gh api -X PUT orgs/northwind/rulesets/1001 --input "$f"
   gh api orgs/northwind/rulesets/1001 --jq .enforcement
   ```
   If you'd rather enforce now without that check, tell me to. The risk is that automation or people pushing directly to these default branches are blocked immediately.

**What I couldn't check**
- **Rule results and audit log:** both requests returned 404, so I have no violation data and no confirmed audit event for the new ruleset.
- **Individual repositories:** repository requests for the four production repositories, `billing-api` and `ledger` also returned 404. Their existing branch protection, default branch names and deployments are unknown.
- **New repositories:** I didn't create a test repository to confirm that a new production one picks up the rule.

**Related gaps (unchanged)**
- `tier` is optional and members can create repositories, so a new production repository with no tier would escape the rule. Making `tier` required would help.
- The rule doesn't require code owner review, re-approval after new pushes, or approval of the latest push by someone else. An approved pull request can therefore receive more commits and still merge. I'd consider turning on stale approval dismissal and latest-push approval.
- It also doesn't explicitly block force pushes or branch deletion.
- I found no drift check; a scheduled comparison of the live ruleset with the committed file would provide one.
