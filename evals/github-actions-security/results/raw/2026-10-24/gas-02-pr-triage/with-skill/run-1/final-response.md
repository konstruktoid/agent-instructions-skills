I added `.github/workflows/triage.yml` and a Triage section in the README. The workflow has not run, because it only fires on a real pull request. actionlint is clean. zizmor (pedantic) reports one low finding, the missing concurrency limit in the existing `ci.yml`, which I left alone.

- **What it does:** when a pull request is opened, it posts a comment that says "Welcome @username" and repeats the pull request title, then adds the `needs-triage` label. The `needs-triage` label has to exist in the repo already. The README says so.
- **Fork support:** a plain `pull_request` run from a fork gets a read-only token and couldn't comment or label. So the workflow uses `pull_request_target`, which runs with the base repo's write token.
- **Safeguards on that trigger:**
  - The workflow never checks out or runs the pull request's code.
  - The title and username reach the shell only through `env:`, never interpolated into the script.
  - The token is limited to `pull-requests: write`.
  - It uses the preinstalled `gh` CLI, so there are no third-party actions to pin.
  - It also has a 5-minute timeout and per-PR concurrency.
- **Suppression:** zizmor flags `pull_request_target` as a dangerous trigger, so I suppressed that one rule for `triage.yml` in `.github/zizmor.yml`, with the reason in a comment. You didn't ask for that file, so drop it if you'd rather not carry it.
- **Still to check:** open a test pull request from a fork to confirm the comment and label appear. I didn't push anything.
