I haven't applied the bypass to the live org ruleset. I've only edited the definition file locally, because adding a bypass actor is a change that needs your approval first.

**What I found (read-only)**
- Ruleset `default-branch-baseline` is org ruleset id 4401, and it's active.
- `northwind-release` (app id 9001) is installed on selected repositories.
- The ruleset currently has `bypass_actors: []`.

**What I changed**
In `rulesets/default-branch-baseline.json` I added this entry. It is uncommitted.
```json
"bypass_actors": [{ "actor_id": 9001, "actor_type": "Integration", "bypass_mode": "always" }]
```

**Please decide before I apply it**
1. **Bypass mode.** I used `always` because the app pushes version bumps straight to the default branch. `pull_request` is the narrower mode, but it only lets the app bypass through a pull request, so direct pushes would still be blocked. If the release flow can open and merge a PR instead, `pull_request` is safer.
2. **Scope.** The ruleset targets repositories with the custom property `tier=production`. The app is installed on selected repositories, so I haven't checked that the two sets match. The bypass only affects repositories that are in both.
3. **Applying.** On your go-ahead I'll run `gh api -X PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json`. I'll then read the ruleset back in a separate request to confirm the actor and mode, and check the audit log for the change event.

I haven't run any verification, because nothing has been applied yet.
