I haven't applied anything. In this session I can't read the skill's `rulesets.md` reference, because the read permission was denied. I also have no shell, so I can't run `gh` to read or change the repository. Here is the proposed ruleset from what I know of GitHub's ruleset schema, for you to approve and apply.

**What I found in the repo**
- There are no `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` or `SECURITY.md` files, so there's no ruleset naming convention to follow.
- The only workflow file is `.github/workflows/deploy.yml`.
- I haven't read the repository's current rulesets, so I don't know whether one already covers `main`.

**Proposed ruleset** (`.github/rulesets/protect-main.json`, so it can be reviewed and reapplied):

```json
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
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

- `non_fast_forward` is the rule that blocks force pushes.
- `required_approving_review_count: 1` requires one approving review.
- I added the following beyond what you asked, to match the skill's baseline:
  - Branch deletion is blocked.
  - Stale approvals are dismissed when new commits are pushed.
  - The most recent push needs an approval.
  - Review conversations must be resolved before merging.
- There are no bypass actors.
- Code owner review is off because the repo has no `CODEOWNERS` file.
- Required status checks are not included. The baseline wants them named and bound to an `integration_id`, and I don't know which checks you use.

**Decisions for you**
1. Do you want the extra rules above kept or removed? Removing them gives exactly the two things you asked for.
2. Which checks should be required on `main`?
3. With one required review, a sole maintainer can't merge their own pull requests. Do you want a bypass actor for that? I'd add one only with a named role and a written reason.

Once you approve, apply it with the command below. I'd then read it back with `gh api repos/OWNER/REPO/rulesets/ID`, run `gh ruleset check --default`, and try a force push to confirm it's rejected.

```sh
gh api -X POST repos/OWNER/REPO/rulesets --input .github/rulesets/protect-main.json
```

If you give me shell access and read access to the skill's reference files, I can write the file and do the apply and verification steps myself.
