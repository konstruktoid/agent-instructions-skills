I added the triage workflow in `.github/workflows/triage.yml` and documented it in the README. It hasn't run on GitHub yet, and nothing is committed or pushed.

**What it does**
- When a pull request is opened, it comments "Welcome, @username, and thank you for your contribution!", followed by the title as a summary. It then applies `needs-triage`.
- It uses `pull_request_target`, because under `pull_request` a fork's token is read-only and couldn't comment or label.
- Its only permission is `pull-requests: write`. It checks out no code and uses no third-party actions, just `gh api`.
- The title is chosen by the contributor, so it never gets parsed by the shell. It's posted as a code block, so a title can't make the bot ping a team or post a link.

**Before you rely on it**
- **Create the `needs-triage` label** in the repository.
- **Merge it to the default branch.** The pull request that adds it won't trigger it.
- **Test from a fork:** after merging, open a pull request from a fork and check for the comment, the label and a green run. That is the only real proof that the permissions are sufficient.

**Checks**
- `actionlint` passed.
- I ran the script steps locally against a stand-in `gh`, using a title full of shell syntax. The title came through as literal text and nothing in it executed.
- `zizmor` (pedantic, offline, so checks that need the GitHub API were skipped) **did not pass cleanly**. It reports two findings:
  - **High, `dangerous-triggers` in `triage.yml`:** this is expected for `pull_request_target`. It's acceptable here because no pull request code is ever run. I didn't suppress it. If you want it silenced, add a `zizmor.yml` entry with that reason.
  - **Low, `concurrency-limits` in `ci.yml`:** this was in a file I didn't change, and I left it alone.

For the pull request description, note that `pull_request_target` and the write permission are deliberate exceptions, for the reasons above. The README lists the rules for editing the workflow safely.
