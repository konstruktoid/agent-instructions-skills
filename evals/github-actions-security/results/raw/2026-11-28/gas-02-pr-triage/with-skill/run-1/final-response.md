I added the triage workflow in `.github/workflows/triage.yml` and documented it in the README. It hasn't run on GitHub, and nothing is committed.

**What it does:** when a pull request is opened, including from a fork, it adds `needs-triage` and then posts a comment welcoming `@username` with the PR title.

**Fork support and its risk**
- It uses `pull_request_target`, because a fork's ordinary `pull_request` run gets a read-only token and can't comment or label.
- That trigger runs with write access, without waiting for maintainer approval. To limit the risk, the job only has `pull-requests: write`, checks out no code and uses no third-party actions.
- The title is passed to the script as data, not pasted into it. In the comment it appears as a code block, so a title can't ping teams or add links under the bot's name.
- Anyone adding a checkout or build step to this workflow later would open a serious hole. The workflow comments and README both warn against it.

**Checks**
- `actionlint` passed.
- I ran both script steps locally with a stand-in for `gh` and a hostile title. Nothing in the title was executed, and it came through as literal text. This didn't test GitHub's permissions or how the comment renders.
- `zizmor` (run offline, pedantic mode) is **not clean**. It reported two findings, and I suppressed neither:
  - **High, `dangerous-triggers` on `triage.yml`:** this is expected, since fork support needs this trigger. If you run `zizmor` in CI later, you could add a suppression with that reason to `zizmor.yml`.
  - **Low, `concurrency-limits` on `ci.yml`:** this is in your existing workflow, which I didn't change.

**Before you rely on it**
1. Create the `needs-triage` label in the repository.
2. Merge the workflow into the default branch. It won't triage the pull request that adds it.
3. Open a test pull request from a fork. Check that the label and comment both appear and the run succeeds. This repository has no remote configured, so I couldn't do that here.
