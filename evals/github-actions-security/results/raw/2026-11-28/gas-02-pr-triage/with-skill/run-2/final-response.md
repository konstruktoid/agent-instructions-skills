I added `.github/workflows/triage.yml` and a "Pull request triage" section to the README. The changes are uncommitted, and the workflow hasn't run on GitHub yet.

**What it does when a pull request is opened:**
- Posts a comment that welcomes the author as `@username` and repeats the title as a summary.
- Adds the `needs-triage` label, even if the comment step fails.

**Working with forks**

It uses `pull_request_target`, because under plain `pull_request` a fork gets a read-only token and couldn't comment or label. This trigger gives a stranger's pull request a run with write access, so I limited it:
- The only permission is `pull-requests: write`.
- It never checks out or runs code from the pull request, and uses no third-party actions or stored secrets.
- The title is passed to the script through an environment variable, so it can't inject shell commands.
- The title appears in the comment as a code block, so a title containing `@org/team` or a link won't ping anyone or render as a link.

**Checks**
- **`actionlint`:** passed.
- **Local test:** I ran both scripts against a stand-in `gh` with a hostile title. The title came through as literal text and nothing in it executed.
- **`zizmor` (offline, pedantic):** not clean; it reported two findings:
  - `dangerous-triggers` (high) on `triage.yml`. This is the `pull_request_target` choice above. I left it visible rather than suppressing it; if your CI should accept it, a `zizmor.yml` entry with the reason would do that.
  - `concurrency-limits` (low) on `ci.yml`. It was there already, and I didn't change that file.

**Before you rely on it**
1. **Create the label:** `gh label create needs-triage --description "Awaiting maintainer triage"`. I couldn't check whether it exists, since the local repository has no remote.
2. **Merge to the default branch:** `pull_request_target` uses the workflow from the base branch, so the pull request that adds it won't trigger it.
3. **Test from a fork:** after merging, open a pull request from a fork and check that both the comment and the label appear. That is the real test of the permissions.
4. **Expect no approval gate:** these runs start even for first-time contributors, so review any later change to this file carefully.

It only runs when a pull request is first opened, not on new commits, title edits or reopening.
