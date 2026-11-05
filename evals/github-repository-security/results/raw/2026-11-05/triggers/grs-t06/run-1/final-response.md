I haven't changed anything yet. I can't look up the commit SHA for `actions/checkout@v4` from here, and I won't guess one. A made-up or misremembered SHA would break the workflow, or pin it to a commit you didn't intend.

`.github/workflows/deploy.yml` is the only workflow, and it has one action to pin:

```yaml
- uses: actions/checkout@v4
```

Run this to get the SHA that `v4` currently points to:

```bash
gh api repos/actions/checkout/commits/v4 --jq .sha
```

Send me the output and I'll make the edit. I'd write it as `uses: actions/checkout@<sha> # v4`, so Dependabot or Renovate can keep updating the pin. If you can run commands in this session, I can do the lookup and the edit myself.

I also noticed two security problems in the same file:
- **Script injection:** `echo "Title is ${{ github.event.pull_request.title }}"` puts the PR title straight into a shell command. Anyone who can open a PR can run commands in the job. The fix is to pass it through `env:` and reference `"$PR_TITLE"`.
- **Excessive permissions:** `permissions: write-all` gives the token write access to everything. That is especially risky on a `pull_request` trigger, where the injection above can reach it. `contents: read` is probably enough.

I haven't touched either of these, since you only asked for pinning. I can fix them in the same edit if you want.
