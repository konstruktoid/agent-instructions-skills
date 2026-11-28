I added `northwind-release` (app id 9001) as a bypass actor on `default-branch-baseline` (ruleset 4401). It's applied to the live org, and reading the ruleset back shows the new entry, with the rules and conditions unchanged. I haven't tested a version-bump push, so rerun the release job to confirm it's unblocked.

I also made the same edit in `rulesets/default-branch-baseline.json`. It isn't committed.

**What this allows**
- **Whole ruleset:** with `bypass_mode: always`, the app can push to default branches without a PR or review. It can also **force-push or delete** those branches, because bypass can't be limited to one rule.
- **Which repos:** the ruleset targets repos with `tier=production`, currently `ingest`, `web`, `infra` and `auth-service`. The bypass works on whichever of these the app can access with write permission. It's installed on selected repos only, and my attempt to list them returned a 404.
- **Credentials:** anyone who can use the app's private key, or change a workflow that uses it, can now get unreviewed code onto those branches. This matters especially for `infra` and `auth-service`.

**Ways to narrow it (not done)**
- **Keep force-push and deletion blocked:** move `deletion` and `non_fast_forward` into a second ruleset with the same conditions and no bypass actors. The app would then bypass only the PR requirement. I recommend this, and can make the change if you like.
- **Limit the app's repos:** check that its installation includes only the repos that need version bumps.
- **Drop the bypass instead:** have the release job open a PR for each bump. This still needs the required code-owner approval each time.

**A separate gap to check**
`billing-api` and `ledger` have the topic `production` but no `tier` property, so this ruleset **doesn't cover them**. If they are production services (payments and finance, going by their topics), they're currently missing these protections from this ruleset. Setting `tier=production` on them would fix that, but could also start blocking pushes there that work today. I left them as they are.

To undo the change, set `bypass_actors` back to `[]` in the file and run:

```
gh api -X PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json
```
