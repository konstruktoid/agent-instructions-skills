I added `northwind-release` (app id 9001) as a bypass actor on `default-branch-baseline` (ruleset 4401), and a read-back of the live ruleset shows it. I haven't tested it with an actual version-bump push.

**Change**
```json
"bypass_actors": [
  { "actor_id": 9001, "actor_type": "Integration", "bypass_mode": "always" }
]
```
Nothing else in the ruleset changed. I also made the same edit in `rulesets/default-branch-baseline.json`; it's uncommitted, so commit it to keep the repo matching what's live.

**What this allows**
- **More than version bumps:** the app can now skip every rule in this ruleset. It can push to default branches without review, and also force-push or delete them.
- **Which repos:** the ruleset targets `tier=production`, which currently means `ingest`, `web`, `infra` and `auth-service`. The bypass applies wherever the app is installed among these, including any repo tagged production later.
- **Key security:** anyone with the app's private key, or a workflow that can create its tokens, gets the same access. Check who that is.

**What I couldn't check**
- **App's repositories:** it's installed on selected repos only, but the lookup for which ones returned 404. If `infra` or others don't need releases, remove them from the installation.
- **Other blockers:** repo-level rulesets and branch protection lookups also returned 404, so I can't confirm whether none exist or I couldn't see them. If the next push is still rejected, check the error for which rule it names.

**Optional tightening**
To stop the app force-pushing or deleting branches, move `deletion` and `non_fast_forward` into a second ruleset with no bypass actors. The app would then bypass only the pull request requirement. I can set that up if you like.

**Separate issue**
`billing-api` and `ledger` have no `tier` property, so this ruleset doesn't cover them at all. If they're production services, their default branches are missing this protection. I didn't change their properties.

To undo the bypass, set `bypass_actors` back to `[]` in the file and run:
```sh
gh api -X PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json
```
