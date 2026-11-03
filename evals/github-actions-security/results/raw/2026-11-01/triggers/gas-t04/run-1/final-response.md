I couldn't create the file. This session doesn't give me a tool that writes files: I can only read and search. Save the content below as `.github/dependabot.yml`:

```yaml
---
version: 2
updates:
  - package-ecosystem: "github-actions"
    # "/" covers .github/workflows/ and any action.yml in the repository root
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    # Wait 7 days before proposing a new release, so a compromised release
    # has time to be noticed before it gets here
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

What each setting does:
- **Weekly schedule:** Dependabot checks every Monday.
- **One grouped PR:** all action updates arrive together in a single weekly PR instead of one PR per action.
- **7-day `cooldown`:** a brand-new release has to have been out for a week before Dependabot proposes it.
- **Labels:** the `dependencies` and `github-actions` labels need to exist in the repo. If they don't, delete the `labels:` block or create the labels first.

I haven't validated this file, and I didn't run `actionlint` or `zizmor`, because I can't run commands here. Dependabot also won't confirm the config works until it's on the default branch.

### Your only workflow has security problems
I read `.github/workflows/deploy.yml` while checking what's already in the repo. It has problems that Dependabot won't fix:

1. **Line 13: `actions/checkout@v4` is pinned to a tag, not a commit SHA.** Tags can be moved to point at different code. Pin it to a full commit SHA with the version in a comment. Dependabot will then keep both the SHA and the comment up to date. It's also probably a few major versions behind.
2. **Line 14: shell injection.** `${{ github.event.pull_request.title }}` is pasted straight into the shell script. Anyone who opens a PR can put a command in the title and it will run. Pass it through `env:` instead:
   ```yaml
   - env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: printf 'Title is %s\n' "$PR_TITLE"
   ```
3. **Line 7: `permissions: write-all`** gives every job full write access. Change it to `permissions: {}` and give the job only `contents: read`.
4. **No `persist-credentials: false` on checkout**, so the token stays in `.git/config` for later steps to read.
5. **No `timeout-minutes` on the job**, so it can run for up to the default 6 hours.

Issues 2 and 3 together are the serious part: any PR author could run commands with a write-scoped token. I'd fix that before anything else. I can draft a hardened `deploy.yml` for you to paste in. To fill in real commit SHAs instead of ones from memory, I'd need to look up the current release with `gh api` or a similar tool, which I can't run here.
