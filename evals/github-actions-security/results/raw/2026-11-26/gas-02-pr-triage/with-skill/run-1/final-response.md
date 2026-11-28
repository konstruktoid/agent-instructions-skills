I added `.github/workflows/triage.yml` and a "Pull request triage" section in the README. Nothing is committed, and the workflow hasn't run on GitHub.

**What it does:** when a pull request is opened, it applies `needs-triage`, then comments with a welcome that mentions the author and repeats the title.

**Fork support:** it uses `pull_request_target`, because under plain `pull_request` a fork's token is read-only and couldn't comment or label. That trigger is risky if misused, so the workflow is limited:
- It never checks out or runs code from the pull request, and uses no third-party actions.
- Its only permission is `pull-requests: write`.
- The title and username are passed as environment variables, so they can't be run as shell code.
- The title appears as a code block, so a title containing `@org/team` or a link won't notify anyone or render.

**Before you rely on it**
1. **Create the label once.** I couldn't check whether it exists, and with these permissions the labelling step may fail if it doesn't. If that step fails, no comment is posted either.
   ```sh
   gh label create needs-triage --description "Awaiting maintainer triage"
   ```
2. **Merge it to `main`.** `pull_request_target` uses the base branch's copy, so the pull request that adds the workflow won't trigger it.
3. **Test from a fork.** After merging, open a pull request from a fork and check for both the label and the comment.

**Checks**
- **`actionlint`:** passed.
- **Local run:** I ran both scripts with a stand-in for `gh` and a title full of shell characters. The title came through as literal text. This doesn't test GitHub permissions or how the comment renders.
- **`make test`:** passed.
- **`zizmor` (1.31.1, pedantic, offline):** not clean, with two findings:
  - **High, `dangerous-triggers` in `triage.yml`:** this is the `pull_request_target` choice explained above. I left it unsuppressed. If `zizmor` gates your CI, I can add a `zizmor.yml` entry with that reason.
  - **Low, `concurrency-limits` in `ci.yml`:** this was in a file I didn't change.

If you open a pull request for this, its description should say why it uses `pull_request_target`.
