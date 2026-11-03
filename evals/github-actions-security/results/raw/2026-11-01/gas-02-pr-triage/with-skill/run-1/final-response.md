I added the triage workflow and documented it in the README, but it has never run on GitHub. I did not push or trigger it. Where I say it works, I'm going by the config and the linters.

`actionlint` is clean. `zizmor` reports two findings:
- **`dangerous-triggers` (high):** this is the `pull_request_target` trigger, which I chose on purpose. A plain `pull_request` run from a fork gets a read-only token and can't comment or label. I left it unsuppressed. A suppression belongs in `zizmor.yml`, which the repo doesn't have, so I didn't add one to get a clean run.
- **`concurrency-limits` (low):** this one is on the existing `ci.yml`, which I didn't touch.

**What it does:** `.github/workflows/triage.yml` runs when a pull request is opened. It posts a comment that welcomes `@<username>` and repeats the title: `Welcome, @user, and thanks for your pull request "<title>". A maintainer will triage it soon.` It then applies `needs-triage`, creating the label first if it doesn't exist.

**Why the trigger is safe here:**
- The workflow never checks out or runs the pull request's code. It only reads event data.
- The title and username go in through `env:` variables, not into the script text.
- It uses only `gh`, so there are no third-party actions to pin.
- Workflow permissions are empty, and the one job gets only `pull-requests: write`.

The README now has a "Triage workflow" section that explains this and warns against adding a checkout of the pull request head.

An unmerged copy can't be checked on a fork. `pull_request_target` runs the workflow from the base branch, so the comment and label only appear once this is on `main`. A pull request opened from a fork after that would be the real test.
