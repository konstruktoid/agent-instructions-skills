Pull request review is not required yet. I created the ruleset in **evaluate mode**, so it logs violations but blocks nothing. The coverage gap below needs your decision before I turn it on.

**What I applied**
- I added `rulesets/production-pr-review.json` and created it as org ruleset `production-pull-request-review` (id 1001).
- It targets the default branch (`~DEFAULT_BRANCH`) of every repo whose `tier` custom property is `production`.
- It requires 1 approving review, dismisses stale approvals on new pushes, requires approval of the latest push, and requires conversations to be resolved. There are no bypass actors.
- I read the ruleset back through a separate request, and every field matches the file.

**Coverage gap**
- Four repos are tagged `tier=production`: `ingest`, `web`, `infra` and `auth-service`.
- `billing-api` and `ledger` have no `tier` value. Both carry a `production` topic (payments and finance), so they look like production repos.
- The ruleset does not reach them yet. I did not set their property, because classifying a repo is a decision for you.

**What I couldn't verify**
- Rule-insights and rule-suite reads returned 404. I therefore couldn't see what evaluate mode would have blocked.
- I haven't confirmed that a newly created repo inherits the tier, and I haven't checked the audit log for the ruleset creation event.

**Decisions for you**
1. Should I set `tier=production` on `billing-api` and `ledger`?
2. Once you've reviewed the evaluate-mode results, should I switch the ruleset to `active`?

Because the ruleset has no bypass actors, a single-maintainer repo could end up unable to merge. Check for that before switching it to active.
