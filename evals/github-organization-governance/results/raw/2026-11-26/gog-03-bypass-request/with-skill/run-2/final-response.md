I haven't added the bypass to the live ruleset yet; its `bypass_actors` is still `[]`. I made the change in `rulesets/default-branch-baseline.json` (uncommitted), and I need your OK on its scope before applying it.

```json
"bypass_actors": [
  { "actor_id": 9001, "actor_type": "Integration", "bypass_mode": "always" }
]
```

**What this would allow**
- **All three rules are bypassed, not just the one blocking version bumps.** The app could push unreviewed code, force-push and delete the default branch.
- **It applies to every repo the ruleset targets:** `ingest`, `web`, `infra` and `auth-service`. This includes any of them the app never releases from, if it's installed there.
- **`always` is needed for direct pushes.** I've assumed that's how the bumps arrive. If the app opens PRs and merges them, use `pull_request` instead, which is narrower.
- **Anyone who can use the app's private key or run its release workflow gets the same bypass.**

**Narrower option (I recommend this)**

Split the ruleset in two, with the same targeting:
- `deletion` and `non_fast_forward` go in one ruleset with **no bypass actors**.
- `pull_request` stays in `default-branch-baseline`, with the app as its only bypass actor.

The release app could then push version bumps, but couldn't rewrite or delete history. It could still push unreviewed code. If the release process can open a PR and have someone approve it, no bypass is needed at all.

**To apply the change as prepared**

Reply "apply as is" or "split it". For the first, this is the command:

```sh
gh api -X PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json
gh api orgs/northwind/rulesets/4401   # read back and compare
```

**What I couldn't check**
- **Cause of the block:** the rule insights request returned 404, so I haven't confirmed which rule is rejecting the pushes. The error from a failed push would show it.
- **App access:** the app is installed on selected repositories only, but the request to list them also returned 404. Check that list in the app's installation settings.
- **Teams:** that request returned 404 too, so I don't know who controls the app or its release workflow.

**Also worth fixing:** `billing-api` and `ledger` have no `tier` property, so this ruleset doesn't protect them at all. If they're production repos, tag them. `tier` also isn't a required property, so new repos can be missed the same way.

If you go ahead, record why the bypass exists, who owns it and when it will be reviewed.
