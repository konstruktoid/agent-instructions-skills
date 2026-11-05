I added northwind-release to `bypass_actors` in `rulesets/default-branch-baseline.json`. I haven't applied it to the live org or committed it, so the app will keep getting blocked until the change is applied.

The new entry is:
```json
{ "actor_id": 9001, "actor_type": "Integration", "bypass_mode": "always" }
```

- **Bypass mode:** I used `always` because version bumps are direct pushes, and `pull_request` mode only lets an actor bypass when it goes through a PR. If the app can open PRs for its bumps, `pull_request` is the narrower choice.
- **Scope:** the app will bypass every rule in the ruleset on the default branch of all `tier=production` repos. That covers the required review, code-owner review, and the deletion and non-fast-forward protections.
- **Applying it:** this changes live org security policy, so I left that step for you to confirm. To apply it, you need the ruleset's ID, which you can get from `gh api orgs/northwind/rulesets`. Then run `gh api -X PUT orgs/northwind/rulesets/<id> --input rulesets/default-branch-baseline.json`. I can run it if you tell me to.
