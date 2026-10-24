I added the triage workflow at `.github/workflows/triage.yml` and documented it in the README. It has not run on GitHub, because that needs a push and a real pull request. actionlint is clean. zizmor reports one remaining low finding, a missing `concurrency` setting in the existing `ci.yml`, which I left alone.

- **What it does:** When a pull request is opened, it comments `Welcome @<user>, … Summary: "<title>"` and adds `needs-triage`. It creates the label first if the repo doesn't have it.
- **Forks:** It uses `pull_request_target`, because a plain `pull_request` run from a fork gets a read-only token and couldn't comment or label. This trigger is risky, so the workflow never checks out or runs pull request code. It only reads the author, title and number from the event.
- **Permissions:** Its only permission is `pull-requests: write`. The title and username go in through `env:` rather than being written into the script. I used the preinstalled `gh` CLI, so no third-party actions are involved.
- **zizmor suppression:** zizmor flags `pull_request_target` as dangerous. I suppressed that one rule for `triage.yml` in a new `zizmor.yml`, with the reason in a comment there.
- **README:** The new section explains the workflow and warns against adding a checkout of the pull request head or any step that runs contributed code.

The first real fork pull request will be the actual test of the comment and the label. I haven't pushed anything or committed.
