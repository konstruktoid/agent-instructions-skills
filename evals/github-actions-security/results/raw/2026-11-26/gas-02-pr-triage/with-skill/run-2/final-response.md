I added the triage workflow in `.github/workflows/triage.yml` and documented it in the README. When a pull request is opened, including from a fork, it applies `needs-triage` and posts a comment welcoming the author by username with the title repeated. It hasn't run on GitHub yet, and nothing is committed or pushed.

**Before you rely on it**
- **Create the label once:** `gh label create needs-triage --description "Awaiting maintainer triage"`
- **Merge it to the default branch first.** The pull request that adds the workflow won't trigger it.
- **Test from a fork:** after merging, open a pull request with a title containing something like `` `x` @someone ``. Check that the label and comment appear and the title shows as plain code.

**The fork trade-off**

A normal `pull_request` run from a fork gets a read-only token, so it can't comment or label. I used `pull_request_target`, which gets a write token, and limited the risk:
- The job never checks out or runs anything from the pull request, and uses no third-party actions.
- Its only permission is `pull-requests: write`.
- The username and title reach the script through environment variables, not pasted into the script text.
- The title appears in a code block, so an outsider can't make the bot ping people or post links.

If you add this to your pull request description, include why it needs `pull_request_target` and the write permission.

**Checks**
- **`actionlint`:** passes.
- **Local script test:** I ran both steps with a fake `gh` and a title full of shell syntax. Nothing in the title was executed. This doesn't test GitHub's permissions or how the comment renders.
- **`zizmor` (offline, pedantic):** it does not pass cleanly, with two findings left:
  - `dangerous-triggers` (high) on `triage.yml`: this is expected because of `pull_request_target`. I didn't suppress it, so if your CI enforces `zizmor`, you'll need to decide whether to add an exception in `zizmor.yml`.
  - `concurrency-limits` (low) on `ci.yml`: this file was already like that, and I didn't change it.

The workflow runs only when a pull request is first opened, not on reopen or new pushes. Manually re-running it would post a second comment.
