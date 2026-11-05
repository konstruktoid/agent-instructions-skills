I've drafted the bypass in `rulesets/default-branch-baseline.json` but haven't applied it to the org. The governance skill treats adding a bypass actor as a proposal that needs explicit approval, and this run has no later turn to ask in.

**What I found**
- `default-branch-baseline` (id 4401) is active. It targets default branches on repos with `tier=production`. It has an empty `bypass_actors` list.
- `northwind-release` (app id 9001) is installed on the org with `repository_selection: selected`.

**Draft change (uncommitted)**
```json
"bypass_actors": [{"actor_id": 9001, "actor_type": "Integration", "bypass_mode": "always"}]
```
I checked that the file is valid JSON.

**Decisions for you**
1. **Bypass mode.** The skill prefers `pull_request` scope. That only lets the app bypass the rules on pull requests it opens, not on direct pushes. Your problem is direct version-bump pushes, so I used `always`. If the app can open and merge a PR instead, `pull_request` is narrower.
2. **App reach.** The app is installed on selected repos only. The bypass applies only where the app has access to a `tier=production` repo, so check that the selection covers the repos you expect.

**To apply, once you approve**
```sh
gh api -X PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json
gh api orgs/northwind/rulesets/4401 --jq .bypass_actors
```
The second command reads the result back. I'd also check the audit log for the ruleset update event.

If you approve the change, tell me the mode you want and I'll apply it and verify it.
