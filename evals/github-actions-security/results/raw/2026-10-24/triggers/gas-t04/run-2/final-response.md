I couldn't create the file. This session only gives me read and search tools, so I had nothing to write with. Save this as `.github/dependabot.yml`:

```yaml
---
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    # Wait a week after a release before proposing it, so a bad or
    # malicious release has time to be noticed and pulled.
    cooldown:
      default-days: 7
    # Combine all action updates into one weekly pull request.
    groups:
      github-actions:
        patterns:
          - "*"
    commit-message:
      prefix: "ci"
    labels:
      - "dependencies"
      - "github-actions"
```

What the settings do:
- **`directory: "/"`**: for this ecosystem, Dependabot looks in `.github/workflows/` (and in `action.yml` at the root) on its own, so you don't need to list the workflows path.
- **`cooldown`**: Dependabot skips any release that is less than 7 days old, which guards against hijacked or broken releases.
- **`groups`**: you get one pull request a week instead of one per action. Remove this block if you'd rather review each action separately.
- **`labels`**: the `dependencies` and `github-actions` labels must exist in the repo. If they don't, Dependabot skips the labels and leaves a comment on the pull request. Remove the block if you don't want labels.

I haven't checked this file with any tool. Once it's on the default branch, the Dependabot tab under the repo's Insights shows whether the config parsed.

**Problems I found in `.github/workflows/deploy.yml`.** Dependabot won't fix any of these:
1. **Line 14 lets a pull request run commands.** `${{ github.event.pull_request.title }}` is pasted into the shell script before it runs, so a pull request title containing shell syntax becomes a command. Pass the title through `env:` and use `"$PR_TITLE"` in the script instead.
2. **Line 7 gives the token every write permission.** `permissions: write-all` is far more than this job needs. Use `permissions: {}` at the top and `contents: read` on the job.
3. **Line 13 points at a tag that can be moved.** `actions/checkout@v4` should be pinned to a full commit SHA with the version in a comment, and should set `persist-credentials: false`. Once it's pinned that way, Dependabot will update both the SHA and the comment.
4. **The job has no `timeout-minutes`**, so it falls back to the 6-hour default.

I can rewrite `deploy.yml` to fix these, but I'd need write access, and pinning needs the current checkout release and its SHA from `gh api`, which I can't run here.
