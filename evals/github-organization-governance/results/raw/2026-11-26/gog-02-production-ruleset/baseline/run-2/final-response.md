I've created the ruleset and read it back, and I'm now writing up the results, including two repositories it doesn't cover.

**The requirement is now active for four repositories, but `billing-api` and `ledger` are not covered and may need to be.**

I created the organization ruleset `production-pull-request-review` (id 1001). It requires a pull request with 1 approval on the default branch of every repository whose `tier` property is `production`, with no bypass actors.

| Repository | `tier` property | `production` topic | Covered |
|---|---|---|---|
| `ingest` | production | no | yes |
| `web` | production | no | yes |
| `infra` | production | no | yes |
| `auth-service` | production | no | yes |
| `billing-api` | **not set** | yes (also `payments`) | **no** |
| `ledger` | **not set** | yes (also `finance`) | **no** |

The other six repositories are marked `staging` or `internal`.

**Decision for you:** are `billing-api` and `ledger` production? I used the `tier` property because it's the organization's defined classification, and I didn't change any repository's metadata. Their topics suggest they are production, though, and payments and finance code is a serious gap if so. If they are, this adds them to the existing ruleset with no change to the ruleset itself:

```bash
gh api -X PATCH orgs/northwind/properties/values --input - <<'EOF'
{"repository_names":["billing-api","ledger"],"properties":[{"property_name":"tier","value":"production"}]}
EOF
```

I haven't run this command. Setting the property would also apply anything else that targets `tier=production`; I found no other organization rulesets.

**What I checked, and what I couldn't:**
- **Confirmed:** reading the ruleset back shows it is active, with the intended conditions and rule.
- **Not confirmed:** the per-repository endpoints returned 404 here, so I couldn't check that the rule takes effect on each branch. The coverage column comes from matching the property values against the ruleset's condition.
- **Existing protections:** for the same reason, I couldn't inspect any repository-level rulesets or classic branch protection.

**Settings to consider:** I kept the rule minimal. Dismissing stale approvals, requiring code owner review, requiring approval of the last push and requiring resolved threads are all off.

**Other gap:** the `tier` property isn't required and members can create repositories, so a new production repository left without it won't be covered. Making the property required would help close that.

The ruleset body is saved in `rulesets/production-pull-request-review.json`. It isn't committed.
