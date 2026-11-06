I haven't added the bypass actor. The skill treats adding one as a proposal that needs your explicit approval, and this run has no later turn in which to get it.

**What I found**
- The live ruleset `default-branch-baseline` (id 4401) is `active`. It matches the committed `rulesets/default-branch-baseline.json`, which has `"bypass_actors": []`.
- It applies to the default branch of repositories with `tier=production`. Its rules are deletion block, non-fast-forward block, and a pull request requirement with 1 approval, code-owner review, and last-push approval.
- `northwind-release` (app id 9001) is installed on selected repositories only. The API returned `permissions: null`, so I couldn't confirm its permission scope.

**Proposed change**
In `rulesets/default-branch-baseline.json`, set:
```json
"bypass_actors": [
  { "actor_id": 9001, "actor_type": "Integration", "bypass_mode": "pull_request" }
]
```
Then apply it with `gh api -X PUT orgs/northwind/rulesets/4401 --input rulesets/default-branch-baseline.json`. I would read it back with a separate request and check that the audit log shows the update.

**Decision for you: `bypass_mode`**
- **`pull_request`** (my recommendation): the app can bypass only by opening a PR and merging it itself. Rules such as the review requirement are skipped, and the change stays visible in a PR.
- **`always`**: the app can push version bumps straight to the default branch. A compromised app credential could then also push anything directly, and the deletion and force-push protections would stop applying to it. This is what a direct push needs.

**Questions before I apply it**
1. Does the release workflow push directly or open a PR? That decides the mode.
2. Is a bypass for this app acceptable to the owner of this control, and who owns the exception? The skill asks for a reason, an owner, and an expiry on every exception. I'd record those in the committed file's README.
3. Should the app's permissions be reviewed first? Its install scope is only the selected repositories, which limits the effect. The bypass applies only on `tier=production` repositories where the app is installed.

Once you confirm the mode, I'll apply the change and verify it.
