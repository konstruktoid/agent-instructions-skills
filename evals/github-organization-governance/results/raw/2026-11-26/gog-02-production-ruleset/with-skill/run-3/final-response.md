**Pull request review is not being enforced yet.** I created the organization ruleset `production-pull-request-review` (id 1001) in **evaluate** mode, so it blocks nothing. It also misses two repositories that look like production.

**What's in place**
- It requires 1 approving review on the default branch of repositories with `tier=production`, with no bypass actors.
- I read it back from GitHub and it matches `rulesets/production-pull-request-review.json`. The file is not committed.

**Coverage**

| Repositories | `tier` | Matched by the ruleset |
|---|---|---|
| `ingest`, `web`, `infra`, `auth-service` | `production` | Yes, by their property value |
| **`billing-api`, `ledger`** | **not set** | **No**, though both have a `production` topic |
| `search`, `mobile`, `notify`, `reports` | `staging` | No |
| `docs`, `sandbox` | `internal` | No |

**Decisions for you**

1. **Are `billing-api` and `ledger` production?** I didn't classify them, because a topic is only a hint and setting the property changes which policies apply to them. If they are, run:
   ```sh
   gh api -X PATCH orgs/northwind/properties/values --input - <<'EOF'
   {"repository_names":["billing-api","ledger"],"properties":[{"property_name":"tier","value":"production"}]}
   EOF
   ```

2. **When should it start blocking?** I started in evaluate mode so you can see what it would block, such as automation that pushes directly to a default branch. After checking the organization's Rules → Insights page, change `"enforcement"` to `"active"` in the file and run:
   ```sh
   gh api -X PUT orgs/northwind/rulesets/1001 --input rulesets/production-pull-request-review.json
   ```
   If you want it blocking now without that observation period, tell me or run the same two steps.

**What I couldn't verify**
- **Evaluate results:** the rule insights request returned 404, so I don't know what the rule would have blocked.
- **Audit evidence:** the audit log request returned 404, so I haven't confirmed that creating the ruleset was logged.
- **Existing protections:** per-repository reads returned 404, so I couldn't check for existing branch protection or repository rulesets.
- **New repositories:** I didn't create a test repository to confirm that a new production repository picks up the rule.

**Follow-ups worth considering**
- **New repositories can slip through.** `tier` is optional and members can create repositories, so a new production service could go unprotected. Making `tier` required would close that gap.
- **Stricter review settings:** stale approval dismissal, code owner review, approval of the latest push and conversation resolution are all off. You asked only for review, but these are worth turning on for production.
