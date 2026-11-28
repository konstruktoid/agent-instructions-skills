I added the triage workflow in `.github/workflows/triage.yml` and documented it in the README. Nothing is committed, and it hasn't run on GitHub.

**What it does:** when a pull request is opened, it applies `needs-triage` and posts a comment that welcomes the author by `@username` and repeats the title as a summary.

**Forks:** it uses `pull_request_target`, because the ordinary `pull_request` trigger only gets a read-only token for fork PRs. The new trigger is risky if misused, so the workflow is limited as follows:
- It never checks out or runs code from the pull request.
- Its only permission is `pull-requests: write`.
- The title and username reach the script as environment variables, so a title can't inject shell commands.
- The title appears in a code block, so it can't `@mention` people or add links to the bot's comment.

**Checks:**
- `actionlint` passed.
- I ran both scripts locally with a stand-in for `gh` and a title full of shell syntax and a line break. Nothing in the title was executed, and it stayed on one line inside the code block.
- `zizmor` reports one high-severity `dangerous-triggers` finding on `pull_request_target`. It flags any use of that trigger, and fork support needs it here. I didn't suppress it, so if your CI runs `zizmor`, you'll need to decide whether to add an ignore comment.

**Before relying on it:**
1. Create the `needs-triage` label in the repository, for example with `gh label create needs-triage`.
2. Merge the workflow into `main`. It only takes effect from the default branch, so the PR that adds it won't be triaged.
3. Open a test PR from a fork and confirm both the label and the comment appear. This is the part I couldn't verify locally.

It runs only when a PR is first opened, not on new commits, title edits or reopening.
