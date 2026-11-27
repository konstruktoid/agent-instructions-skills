I added `.github/workflows/triage.yml` and documented it in the README. When a pull request is opened, including from a fork, it applies `needs-triage` and then posts a comment that welcomes `@author` and repeats the title. Nothing is committed.

**Before you rely on it**
- **Create the label first:** `gh label create needs-triage --description "Awaiting maintainer triage"`. The job only has `pull-requests: write`, which may not be enough to create a missing label. If the label step fails, no comment is posted either.
- **Merge it to the default branch:** `pull_request_target` uses the workflow from the base repository, so the PR that adds it won't trigger it. After merging, open a test PR from a fork.

**Fork support and security**
A plain `pull_request` trigger gets a read-only token on fork PRs, so commenting and labelling would fail. I used `pull_request_target`, which has write access even for a stranger's PR, with these limits:
- It never checks out or runs code from the pull request, and uses no third-party actions.
- The job's only granted permission is `pull-requests: write`.
- The title and username reach the script through environment variables, so the shell doesn't run anything in them.
- The title is shown as a code block, so a title containing `@org/team`, links or Markdown can't ping people or change the comment's layout.

**Checks run**
- `actionlint` passes and `make test` passes (it only prints "tests pass").
- I ran both scripts locally against a stand-in `gh` with a hostile title. Nothing in the title was executed, and line breaks were flattened to spaces.
- `zizmor` reports one high finding, `dangerous-triggers`, because of `pull_request_target`. It flags the trigger itself, which fork support needs here. I didn't suppress it, so if you add `zizmor` to CI you'll need to accept it explicitly.
- Nothing has run on GitHub, so the token permissions and a real fork PR are still untested.

The workflow only runs when a PR is first opened, not on reopening or later pushes. The README says so, along with the rules to follow when editing the workflow.
