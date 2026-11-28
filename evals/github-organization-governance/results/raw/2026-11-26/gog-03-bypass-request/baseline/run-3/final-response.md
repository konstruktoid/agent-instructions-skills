I added `northwind-release` (app id 9001) as a bypass actor on `default-branch-baseline` (ruleset 4401), and reading the ruleset back confirms it's there. I haven't tested a version-bump push, so I can't yet say the blocking is gone.

**What changed**
- The only change is the new entry: `actor_type: Integration`, `bypass_mode: always`. Rules, conditions and enforcement are as before.
- I updated `rulesets/default-branch-baseline.json` to match. It isn't committed.

**What this allows**
The bypass covers the whole ruleset, not just the review requirement. On the default branch of every repo it targets, the app can now:
- push without a pull request or code owner review
- force-push
- delete the branch, as far as this ruleset is concerned

Going by the `tier=production` property, the targeted repos are `ingest`, `web`, `infra` and `auth-service`. Anyone who can get a token for the app has the same access, so check who holds its private key and which workflows use it.

**A tighter option**
If the app only needs to push version bumps, split the ruleset in two:
- **Pull request rule:** keeps the app's bypass.
- **Deletion and force-push rules:** go in a second ruleset with the same targeting and no bypass.

I can do that if you like. Create the second ruleset before removing those rules from the first, so there's no gap in protection.

**Worth checking: two repos may be unprotected**
`billing-api` and `ledger` have the topic `production` but no `tier` property. The ruleset selects on the property, not topics, so it doesn't appear to cover them. That was already true before this change. If they should be covered, set `tier=production` on both. The app would then get its bypass there too. I haven't changed either one.

**If the app is still blocked**
- I couldn't check repo-level rulesets or branch rules, because those requests returned 404. A separate rule there could still block the push.
- I also couldn't list which repos the app is installed on. It's limited to selected repos, so confirm that includes the ones it releases from.

To undo the change, set `bypass_actors` back to `[]` in the file and run:

```
gh api --method PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json
```
