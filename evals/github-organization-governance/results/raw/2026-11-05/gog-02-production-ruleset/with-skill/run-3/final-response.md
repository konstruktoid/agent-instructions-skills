I created an organization ruleset that requires pull request review on the default branch of the four repositories tagged `tier=production`: `ingest`, `web`, `infra` and `auth-service`. `billing-api` and `ledger` are not covered yet, because they have no `tier` value.

I did not guess a tier for those two. Their names suggest they are production, and both are private. If you confirm, setting `tier=production` on each will bring them under the ruleset automatically.

**The ruleset**
- It is named `production-pull-request-review` (id 1001) and is saved in `rulesets/production-pull-request-review.json`.
- It targets `~DEFAULT_BRANCH` on repositories with the custom property `tier=production`, not a list of names, so new production repositories pick it up.
- It requires one approving review. A new push dismisses earlier approvals, the most recent push must be approved, and review threads must be resolved.
- I left out code owner review so it can't block repositories that have no CODEOWNERS file. There are no bypass actors.

**Verification**
- I created the ruleset in evaluate mode, then switched it to active. I read it back in a separate request and the enforcement, conditions and rules match what I intended.
- I could not read rule insights: the rule-suites endpoint returned 404. I switched to active without reviewing any evaluate-mode violations, so I don't know whether the ruleset blocks existing automation. Please watch the first pushes to the four repositories.
- I did not confirm that a newly created production repository inherits the ruleset, and I did not confirm that an audit log event was recorded.
- I did not create a committed drift check. The ruleset definition is in the file above and has not been committed to git.
- Not checked: archived repositories (none exist in the organization), enterprise-level policy, and the other baseline items such as base permissions, two-factor authentication and Actions policy.
