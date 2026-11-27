I prepared the bypass entry but **haven't applied it**, so `northwind-release` is still blocked. It exempts the app from more than version bumps, so please confirm that scope first.

**The change** (uncommitted, in `rulesets/default-branch-baseline.json`):

```json
"bypass_actors": [
  { "actor_id": 9001, "actor_type": "Integration", "bypass_mode": "always" }
]
```

**What it allows**
- The app could push to the default branch without a pull request, and also **force-push or delete it**. A bypass covers every rule in the ruleset, not just the one blocking you.
- It would apply on the repositories tagged `tier=production` that the app can access. The ruleset currently targets `auth-service`, `infra`, `ingest` and `web`.
- Anyone who can use the app's private key, or change a workflow that uses it, would get the same powers.
- I used `always` because `pull_request` mode wouldn't permit a direct push.

**A narrower option, which I recommend**
Split the ruleset in two:
- `deletion` and `non_fast_forward` stay in `default-branch-baseline`, with no bypass.
- `pull_request` moves to a new ruleset with the same targeting, where the app is the only bypass actor.

Version bumps would go through, and the app still couldn't force-push or delete the branch. Create the new ruleset before removing the rule from the old one, so there's no gap in protection.

**To go ahead**, reply "split it" and I'll prepare and apply that. If you want the single-ruleset version as drafted, reply "apply as is", or run:

```sh
gh api -X PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json
gh api orgs/northwind/rulesets/4401 --jq '{enforcement, bypass_actors, rules}'
```

**What I checked and couldn't check**
- The live ruleset is still active with no bypass actors.
- App 9001 is installed on selected repositories, but I couldn't read which ones (404). Check that it covers only the repositories that release through it.
- Rule insights returned 404, so I haven't confirmed that this ruleset, or which of its rules, is blocking the pushes. Look at a failed push's error first. Repository-level protection could also be blocking, and this change wouldn't fix that.
- The audit log read also returned 404. After applying, confirm the `repository_ruleset.update` event in the settings UI.

**Separate gap:** `billing-api` and `ledger` have no `tier` property, so this ruleset doesn't protect them. If they're production services, they should be tagged. Check first whether the release app pushes to them, since tagging would start blocking it there too until the bypass is in place.

If you approve a bypass, record an owner, a reason and a review date for the exception. I don't have those yet.
