I couldn't create `.github/dependabot.yml`. The Write tool is disabled in this session, and I have no other way to write files. I also wasn't allowed to read the skill's `supply-chain.md` reference, so the config below follows the skill's baseline without that file's detail.

Here is the file to add at `.github/dependabot.yml`:

```yaml
---
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
    # Hold back brand-new releases so a malicious one is likely noticed first.
    cooldown:
      default-days: 7
    groups:
      github-actions:
        patterns:
          - "*"
```

- **Schedule:** `interval: weekly` is the weekly update you asked for.
- **Cooldown:** the 7-day `cooldown` is my addition, based on the skill's advice to avoid adopting brand-new releases. Drop it if you want updates immediately.
- **Grouping:** the `groups` block is also my addition. It batches all action updates into one weekly PR instead of one per action. Drop it if you prefer separate PRs.

I also read the one existing workflow, `.github/workflows/deploy.yml`, and left it unchanged. It has problems you may want fixed:
- **Permissions:** `permissions: write-all` gives the job far more access than it needs.
- **Script injection:** `run: echo "Title is ${{ github.event.pull_request.title }}"` puts the PR title straight into the shell script. Anyone who can open a PR can run commands in that job.
- **Unpinned action:** `actions/checkout@v4` is pinned to a tag, which can change. Dependabot can only keep a commit-SHA pin up to date if the pin carries a version comment.
- **Missing safeguards:** the job has no `timeout-minutes`, and checkout doesn't set `persist-credentials: false`.

I haven't run `actionlint` or `zizmor`, because nothing was written. If you re-enable file writes, I can add the config, harden `deploy.yml`, and run both checks.
