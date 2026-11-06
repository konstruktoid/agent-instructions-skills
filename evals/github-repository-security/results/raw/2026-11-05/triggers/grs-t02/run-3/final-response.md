I haven't applied anything. I have no shell here, so I can't run `gh` to read or change the repository. The permission to read the skill's `references/rulesets.md` was also denied. The repo has no `CLAUDE.md`, `CONTRIBUTING.md`, `SECURITY.md` or ruleset JSON to follow. Its only `.github` file is `.github/workflows/deploy.yml`.

The skill says to read the current state first, and I couldn't. I don't know the `OWNER/REPO`, whether a ruleset or branch protection already covers `main`, or whether the organization sets rules of its own. Please run this and share the output:

```sh
gh ruleset list --repo OWNER/REPO --limit 100
gh api repos/OWNER/REPO/branches/main/protection
```

**Proposed ruleset** (`main-protection`, target `branch`, enforcement `active`, no bypass actors):

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
        "required_review_thread_resolution": true
    } }
  ]
}
```

- **What you asked for:** `non_fast_forward` blocks force pushes to `main`, and `required_approving_review_count: 1` requires one approving review.
- **What I added:** I also block deletion, dismiss stale approvals on a new push, require approval of the most recent push, and require conversation resolution. The skill's baseline asks for these, but you didn't. I can drop them.
- **Not included:** The baseline also wants named status checks bound by `integration_id`, and code owner review. I left both out because the repo has no `CODEOWNERS`, and I don't know which checks it runs.
- **Bypass:** I've set none, which matches the baseline.
- **Reviewability:** I'd commit the JSON to the repo, for example as `.github/rulesets/main-protection.json`, so it can be reviewed and reapplied.

**To apply it:** Reply with the `OWNER/REPO` and say whether to go ahead. If you grant me shell access, I'll create the ruleset with `gh api -X POST repos/OWNER/REPO/rulesets --input ...`. Then I'll read it back with `gh api repos/OWNER/REPO/rulesets/ID` and run `gh ruleset check --default`. A real force push or an unreviewed pull request would show whether it blocks them.
