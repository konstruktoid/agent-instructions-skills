I added the triage workflow and documented it in the README. It has not been run on GitHub, so I haven't seen it post a comment or apply the label. A fork pull request would exercise it: opening one against the default branch should produce the welcome comment and the label.

**What it does**
- **Trigger:** `.github/workflows/triage.yml` runs on `pull_request_target`, type `opened`. I chose that over `pull_request` because fork pull requests get a read-only token under `pull_request`, which can't comment or label.
- **Steps:** one `gh` script creates the `needs-triage` label if it doesn't exist and applies it. It then posts a comment that welcomes `@username` and repeats the pull request title.
- **Safety:** it never checks out or runs pull request code. The title, username and number reach the script through `env:` variables, not `${{ }}` inside the script. The token holds only `pull-requests: write`, and the job has a timeout and a concurrency group.
- **README:** a new "Triage workflow" section explains the behaviour and warns against adding a checkout of the pull request head.

**Checks**
- `actionlint` is clean.
- `zizmor --persona=pedantic` has one remaining low finding, a missing concurrency setting in the existing `ci.yml`. I left that file alone.
- zizmor flagged `pull_request_target` as a dangerous trigger. I added `zizmor.yml` to ignore that rule for `triage.yml` only, with a comment giving the reason. That file is new in the repository, so drop it if you'd rather not carry it.

I didn't push anything or commit.
