I added `.github/workflows/triage.yml` and a "Triage workflow" section in the README. I haven't run it on GitHub, so it's untested end to end. The `needs-triage` label has to exist in the repo first, or the labeling step will fail. The README says so.

**What it does:** when a pull request is opened, it posts a comment like `Welcome @user, and thanks for opening "<title>". A maintainer will triage it soon.` It then adds the `needs-triage` label.

**Fork support:** the workflow uses `pull_request_target`. A plain `pull_request` run from a fork gets a read-only token, which can't comment or label. To keep that trigger safe:
- The workflow never checks out or runs pull request code.
- It reads only the PR number, author and title.
- Those go in through `env:` rather than being interpolated into the script.
- The job holds only `pull-requests: write`.
- It uses the preinstalled `gh` CLI, so there are no third-party actions to pin.

**Checks:**
- `actionlint` is clean.
- `zizmor` (pedantic) reports one `dangerous-triggers` error on `pull_request_target`. That trigger is the deliberate choice above, and a YAML comment in the workflow gives the reason. I didn't add a suppression config, so you can decide whether to.
- `zizmor` also flags a missing `concurrency` setting on the existing `ci.yml`. I left that file alone.

I added per-PR `concurrency` to the new workflow to clear the same warning there.

**Comment content:** the PR title appears verbatim in the comment, so a title containing `@someone` will notify that person.

I haven't committed anything.
