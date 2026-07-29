## Summary

Added `.github/workflows/triage.yml`, a workflow that fires on `pull_request_target` (`opened`), and:
- Posts a comment welcoming the contributor by `@username` and repeating the PR title.
- Applies the `needs-triage` label.

**Fork-safety design:** contributions arrive from forks, and a plain `pull_request` trigger gets a read-only token for fork PRs — it can't comment or label. `pull_request_target` gives a writable token, but per the skill's guidance that's only safe if no fork-controlled code is ever executed. This workflow does no checkout at all — it reads only event metadata (PR number, author, title) and calls the GitHub API via `gh`, with every value passed through `env:` (never interpolated into the shell via `${{ }}`) to avoid script injection.

**Verification:**
- `actionlint`: clean (exit 0).
- `zizmor --persona=pedantic`: went from 4 findings → 1 across one fix cycle (added a concurrency group, commented the permission). The one remaining finding (`dangerous-triggers` on `pull_request_target`) is an inherent, deliberate exception — documented with a YAML comment on the trigger line and in the README, per the skill's rule for stated exceptions rather than something to suppress.
- The workflow was **not executed live** — this repo has no git remote, so there's no GitHub Actions runner to trigger it against. Static verification (actionlint + zizmor) is what I could confirm; treat this as unexecuted until run in a real repo.

Also updated `README.md` with a "Workflows" section documenting both `ci.yml` and the new `triage.yml`, including the note that the `needs-triage` label must exist in the repository beforehand.
