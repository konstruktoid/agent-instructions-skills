**I haven't added the bypass yet; the live `default-branch-baseline` ruleset (id 4401) is unchanged.** A direct version-bump push needs `bypass_mode: always`. On this ruleset, that would also let the app force-push to and delete the default branch of every production repo: `ingest`, `web`, `infra` and `auth-service`. A version bump needs neither, so I've prepared a narrower version for you to approve.

**Recommended: split the ruleset** (files in `proposals/release-app-bypass/`, uncommitted)
- `default-branch-integrity` (new) blocks deletion and force pushes, with no bypass.
- `default-branch-baseline` keeps the pull request rule, with app 9001 as its only bypass actor.

To apply it, create the new ruleset first so no protection lapses:

```sh
cd proposals/release-app-bypass
gh api -X POST orgs/northwind/rulesets --input default-branch-integrity.json
# read it back and confirm it's active with both rules, then:
gh api -X PUT orgs/northwind/rulesets/4401 --input default-branch-baseline.json
gh api orgs/northwind/rulesets/4401
```

Then move both files into `rulesets/` so the committed definitions match what's live.

**If you want exactly what you asked for**, with the app bypassing all three rules, run this from the repo root:

```sh
jq '.bypass_actors=[{"actor_id":9001,"actor_type":"Integration","bypass_mode":"always"}]' \
  rulesets/default-branch-baseline.json > /tmp/baseline-bypass.json
gh api -X PUT orgs/northwind/rulesets/4401 --input /tmp/baseline-bypass.json
gh api orgs/northwind/rulesets/4401
cp /tmp/baseline-bypass.json rulesets/default-branch-baseline.json
```

You can also reply "apply the split" or "apply as asked" if you can continue this session.

**Before you approve**
- **What the bypass allows:** with either option, the app can push any change, not only version bumps, to those default branches without review. Anyone holding its private key can do the same.
- **Alternative with less access:** have the release workflow open a pull request for the bump. With `bypass_mode: pull_request`, the app could merge it without review but couldn't push directly.
- **Cause not confirmed:** rule insights and the audit log both returned 404, so I couldn't see which rule is blocking the pushes. The pull request rule is the likely one. If the release job force-pushes, the split won't unblock it.
- **App reach:** it's installed on selected repositories, but I couldn't read which ones or what permissions it has.
- **Owner and expiry:** the exception needs both; they're left blank in the proposal's README.

**Separate gap:** `billing-api` and `ledger` have no `tier` property, so this ruleset doesn't apply to them at all. The property isn't required, so new repos can miss it too. If those two are production services, they currently lack these protections from this ruleset. Tagging them `production` would also bring them under whichever bypass you choose.

The live ruleset matches the committed `rulesets/default-branch-baseline.json`.
