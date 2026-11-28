I added `.github/workflows/triage.yml` and a "Pull request triage" section in the README. When a pull request is opened, the workflow posts a welcome comment with the author's username and the PR title, then applies `needs-triage`. Nothing is committed.

**Before it will work**
- Create the label once: `gh label create needs-triage --description "Awaiting triage"`. I couldn't check whether it already exists, since the repo has no remote.
- Merge the workflow into `main`. It won't run on the PR that adds it.

**Fork support and safety**

It uses `pull_request_target`, because the ordinary `pull_request` event gives fork PRs a read-only token that can't comment or label. The catch is that the workflow runs with write access even for strangers' PRs, so I limited it:
- It never checks out or runs code from the PR, and uses no third-party actions.
- Its only permission is `pull-requests: write`.
- The title and username reach the script as environment variables, so a title can't inject shell commands.
- The title appears in the comment as a code block, so it can't ping people or add links in the bot's name. The author is still @-mentioned in the greeting.

**Checks**
- **Script test:** I ran both steps locally against a stand-in `gh`, using a title full of shell syntax, Markdown and line breaks. Nothing in it was executed, and it stayed on one line inside the code block.
- **`actionlint`:** passed.
- **`zizmor`:** reports one high-severity `dangerous-triggers` finding, which flags any use of `pull_request_target`. It's expected here, and I didn't suppress it. If your CI runs `zizmor` as a gate, you'd need to add an ignore comment with the reason.

I haven't run it on GitHub. After merging, open a test PR from a fork and check that both the comment and the label appear.
