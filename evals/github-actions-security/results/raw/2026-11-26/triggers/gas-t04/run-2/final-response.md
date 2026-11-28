I couldn't create the file. This session has no tool that can write files or run commands, so I can only read the repo. Here is the configuration to save as `.github/dependabot.yml`:

```yaml
---
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    cooldown:
      default-days: 7
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

- **`directory: "/"`**: Dependabot checks `.github/workflows/` and any `action.yml` from the repository root.
- **`cooldown`**: Dependabot won't suggest a release until it has been out for 7 days. That gives time for a compromised or broken release to be caught before it reaches you.
- **`groups`**: all action updates arrive as one weekly pull request instead of one per action.
- **Labels**: Dependabot can only apply labels that already exist in the repo. If `dependencies` and `github-actions` don't exist yet, create them or delete that block.

I haven't run `actionlint` or `zizmor`, and I couldn't read the skill's supply-chain reference file because access was denied.

## Problems in `.github/workflows/deploy.yml`

I noticed these in the one existing workflow and didn't change it:

1. **`actions/checkout@v4` uses a tag, not a commit SHA.** Dependabot will still bump the tag, but tags can be moved to point at different code. It should be pinned to a full commit SHA with a `# vX.Y.Z` comment, and Dependabot keeps that format up to date. I couldn't look up the current SHA without shell access.
2. **`permissions: write-all` (line 7)** gives every job full write access, on a workflow that runs on pull requests. It should be `permissions: {}`, with `contents: read` granted only to the job.
3. **Script injection (line 14):** `${{ github.event.pull_request.title }}` is pasted straight into the shell command, so whoever opens a pull request can run commands by choosing its title. Pass it through `env:` and print `"$PR_TITLE"` instead.
4. The checkout step lacks `persist-credentials: false`, so the token stays in `.git/config` for later steps. The job also has no `timeout-minutes`, so it can run for up to 6 hours.

If you allow file writes, I can add the Dependabot file and fix `deploy.yml`, then run `actionlint` and `zizmor` on the result.
