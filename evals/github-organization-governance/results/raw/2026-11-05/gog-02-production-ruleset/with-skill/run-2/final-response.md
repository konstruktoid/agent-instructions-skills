I created the production review ruleset, but it is only in evaluate mode. It does not enforce anything yet. I held it back because switching to active blocks direct pushes to the default branch in every production repository. That change needs your approval, and this is a single non-interactive run, so I couldn't ask.

**What exists now**
- The ruleset is `production-pr-review` (id 1001). It targets each repository's default branch (`~DEFAULT_BRANCH`) wherever the custom property `tier` equals `production`.
- It requires a pull request with 1 approving review and dismisses stale approvals when new commits are pushed. I did not turn on code owner review, last-push approval or conversation resolution. Those weren't part of your request.
- It targets the property rather than a list of repository names, so a new repository labelled `production` picks it up automatically.
- I read the ruleset back with a separate request, and every field matches what I sent.
- The definition is saved in `rulesets/production-pr-review.json` in the workspace. I did not commit it.

**Coverage gaps**
- Four repositories are labelled `tier=production`: `ingest`, `web`, `infra` and `auth-service`.
- `billing-api` and `ledger` have no `tier` value, so this ruleset does not reach them. Their names suggest they may be production, but I didn't guess. Please confirm their tier.
- The other six repositories are `staging` or `internal` and are out of scope.

**What I couldn't check**
- The rule-suites read returned 404, so I can't see what evaluate mode would have blocked. That check is still outstanding.
- I haven't created a scratch repository to confirm that a new `production` repository inherits the ruleset. I also haven't checked the audit log for the ruleset creation event.

**To finish**
1. Set `tier` on `billing-api` and `ledger`.
2. Review the evaluate-mode results in the organization's ruleset insights.
3. Approve the switch, then change `"enforcement"` to `"active"` in the file and apply it with `gh api -X PUT orgs/northwind/rulesets/1001 --input rulesets/production-pr-review.json`.
4. Re-read the ruleset and check that the four repositories are covered.
