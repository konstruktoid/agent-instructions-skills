I added `.github/workflows/triage.yml` and a Triage section in the README. When a pull request is opened, including from a fork, it posts a welcome comment with the author's username and the PR title, then adds `needs-triage`. It hasn't run on GitHub yet, and nothing is committed.

**Before it works**
1. Create the label: `gh label create needs-triage`. The workflow's token is limited to pull request writes, so don't rely on it to create the label.
2. Merge the workflow into `main`. It won't run for the PR that adds it, so test it afterwards by opening a PR from a fork.

**Security choices**
- **Trigger:** it uses `pull_request_target`, because a normal `pull_request` run from a fork gets a read-only token and couldn't comment or label.
- **No fork code:** it never checks out or runs anything from the pull request, uses no third-party actions, and has only `pull-requests: write`.
- **Title handling:** the title is passed through an environment variable, so it isn't run as shell code. It appears in the comment as a code block, so it can't ping people or add links or formatting.

**Checks**
- **`actionlint`:** passed.
- **Comment step:** I ran it locally with a stand-in for `gh` and a title containing quotes, `$(id)`, backticks, an `@` mention and a line break. It all came through as literal text on one line.
- **`zizmor` (pedantic, offline, so some online audits were skipped):** it did not pass cleanly, with two findings:
  - `dangerous-triggers` (high) on `triage.yml`: this is the expected result of using `pull_request_target`. I explained it in the workflow and README rather than suppressing it. If your CI later requires a clean run, you could add an exception with that reason to `zizmor.yml`.
  - `concurrency-limits` (low) on `ci.yml`: this was already there, and I didn't change that file.

The comment will also be posted on pull requests opened by bots such as Dependabot. If you'd rather skip those, it's a one-line condition on the job.
