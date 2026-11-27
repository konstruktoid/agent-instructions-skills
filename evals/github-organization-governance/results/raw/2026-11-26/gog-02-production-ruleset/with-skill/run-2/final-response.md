**Pull request review is not being required yet.** I created the ruleset in northwind, but in evaluate mode, so it blocks nothing until you switch it to active.

**What's in place**
- The ruleset is `production-pull-request-review` (id 1001). It applies to the default branch of every repository with `tier=production`.
- It requires a pull request with 1 approval and has no bypass actors.
- I read it back separately and it matches `rulesets/production-pull-request-review.json`, which is new and uncommitted.

**Coverage**

| `tier` value | Repositories |
|---|---|
| `production` (targeted) | `ingest`, `web`, `infra`, `auth-service` |
| `staging` or `internal` (not targeted) | `search`, `mobile`, `notify`, `reports`, `docs`, `sandbox` |
| **none (missed)** | **`billing-api`, `ledger`** |

**Decisions for you**

1. **Are `billing-api` and `ledger` production?** Their names suggest they might handle money, but that isn't evidence, and I couldn't read anything else about them. If either is production, "every production repository" isn't met until it has `tier=production`. Tell me which, and I can set it.

2. **Should I switch to active?** I left it in evaluate mode so you can see what it would block first, such as release bots or scripts that push straight to the default branch. The rule results request returned 404, so I have no violation data; that is not a clean result. Check Rule Insights in the organization settings after some normal activity. If you'd rather enforce now, change `"enforcement"` to `"active"` in the file, then run:
   ```sh
   gh api --method PUT orgs/northwind/rulesets/1001 --input rulesets/production-pull-request-review.json
   ```
   Also check that each production repository has at least two people who can write to it, since authors can't approve their own pull requests.

**Not verified**
- **Existing protection:** there were no organization rulesets before this one. Repository rulesets and branch protection returned 404, as did the other per-repository requests, so I don't know what each repository already enforces.
- **Default branches:** the repository list shows `default_branch` as null for all 12. I couldn't confirm which branch the rule resolves to in any of them.
- **Audit and inheritance:** the audit log returned 404, so I have no audit entry for the creation. I also didn't create a test repository to check that new ones pick up the rule.

**Gaps to close next**
- **New repositories:** `tier` is optional and members can create repositories, so a new production service could go untagged and be skipped. Making `tier` required would help.
- **Stronger review:** stale approvals aren't dismissed, and code owner review, approval of the latest push and conversation resolution are all off. I kept to what you asked; I'd consider turning on stale dismissal and latest-push approval, since without them code can be added after approval.
- **Drift:** nothing yet checks on a schedule that the live ruleset still matches the file.
