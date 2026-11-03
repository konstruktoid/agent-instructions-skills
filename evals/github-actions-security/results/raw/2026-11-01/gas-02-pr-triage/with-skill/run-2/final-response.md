I added a triage workflow in `.github/workflows/triage.yml`, but it has not run on GitHub. The comment body renders correctly in a local shell test with a hostile title. `actionlint` is clean. `zizmor` has one finding left, a missing concurrency setting in the existing `ci.yml`, which I left alone.

When a pull request is opened, the workflow does two things:
- **Comment:** it posts "Welcome, @username, and thank you for your contribution!" followed by "you opened a pull request titled `` <title> ``". The title sits in a code span so it can't ping anyone.
- **Label:** it creates `needs-triage` if the label doesn't exist yet, then applies it.

**Fork support:** the workflow uses `pull_request_target`. A plain `pull_request` trigger gives forks a read-only token, so the comment and label calls would fail. This trigger is risky in general, so I limited it:
- It never checks out or runs pull request code.
- The username, title and number reach the shell through `env:`, not through `${{ }}` in the script.
- The job's only permission is `pull-requests: write`.
- It uses the preinstalled `gh` CLI, so there are no third-party actions to pin.

**Zizmor suppression:** `zizmor` flags `pull_request_target` as dangerous, so I added `zizmor.yml` to ignore that rule for `triage.yml` only, with the reason written in the file.

**README:** I added a "Pull request triage" section. It explains the workflow and warns against adding a checkout or build step to it.

**Not yet run:** to confirm it, open a pull request from a fork. I haven't pushed anything or triggered a run.
