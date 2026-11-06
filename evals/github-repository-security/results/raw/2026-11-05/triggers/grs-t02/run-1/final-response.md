I haven't applied anything yet. Two things blocked me:

- **No shell.** I can't run `gh` here, so I can't read the repo's current rulesets or apply a new one.
- **Reference file unreadable.** I wasn't granted read access to the skill's `references/rulesets.md`, so I haven't checked the proposal against it.

The repo has no `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md` or ruleset JSON. The only file under `.github/` is `workflows/deploy.yml`. So there's no existing ruleset naming convention to follow.

**Proposed ruleset** (`main-protection`, target `branch`, enforcement `active`, applied to `~DEFAULT_BRANCH`):

```json
{
  "name": "main-protection",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [],
  "rules": [
    { "type": "non_fast_forward" },
    { "type": "deletion" },
    { "type": "pull_request", "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_last_push_approval": true,
        "require_code_owner_review": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["merge", "squash", "rebase"]
    } }
  ]
}
```

- **What you asked for:** `non_fast_forward` blocks force pushes to `main`. `pull_request` with `required_approving_review_count: 1` requires one approving review.
- **What I added from the security baseline:** blocking branch deletion, dismissing stale approvals on a new push, requiring approval of the most recent push, and requiring conversation resolution. Tell me if you'd rather keep it to just the two rules you named.
- **Left out on purpose:**
  - **Required status checks:** the baseline wants them bound by `integration_id`, but I don't know which checks this repo reports.
  - **Code owner review:** there's no `CODEOWNERS` file yet.
  - **Bypass actors:** none, so admins are bound by the rules too.
- **Replaces:** I haven't been able to read the current state, so I don't know whether `main` already has branch protection or a ruleset.

**What I need from you:**
1. Approval of the ruleset above, with or without the extras.
2. Shell access for `gh` (or read access to the skill references), and the `OWNER/REPO` slug.

Once I can run `gh`, I'll read the current rulesets, save the JSON to the repo, apply it, and read it back with `gh api repos/OWNER/REPO/rulesets/ID` and `gh ruleset check --default`. Neither force pushes nor reviews have been tested against the real branch. A rejected force push and a blocked unreviewed merge are the events that would confirm it.
