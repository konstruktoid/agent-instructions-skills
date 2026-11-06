I added northwind-release to `bypass_actors` in `rulesets/default-branch-baseline.json`. I haven't applied it to the org, so the app will keep getting blocked until someone applies it.

```json
"bypass_actors": [
  { "actor_id": 9001, "actor_type": "Integration", "bypass_mode": "always" }
]
```

- **Bypass mode:** I used `always` because the app pushes version bumps straight to the default branch. `pull_request` mode only lets an actor bypass through a PR, so direct pushes would still be blocked. If you'd rather the app open and merge PRs, `pull_request` is the narrower choice.
- **Scope:** The ruleset covers the default branch of every repo with the property `tier=production`. This change lets the app skip the review, code-owner and last-push-approval requirements on all of those repos. The deletion and non-fast-forward rules are bypassed too.
- **Applying it:** This is a live change to org-wide protection, so I want your go-ahead first. Once you confirm, I'll look up the ruleset ID and apply the file with `gh api --method PUT orgs/northwind/rulesets/<id> --input rulesets/default-branch-baseline.json`.
