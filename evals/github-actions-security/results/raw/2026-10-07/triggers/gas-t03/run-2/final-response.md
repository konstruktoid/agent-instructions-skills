I haven't changed anything yet. The workflow has one action to pin, `actions/checkout@v4` in `.github/workflows/deploy.yml`. Pinning it needs a real commit SHA, and I can't look one up here because the Bash tool is disabled, so I can't run `gh api`. I won't write a SHA from memory. A made-up or stale one would either break the workflow or point at the wrong commit.

You can resolve it yourself with:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name
gh api repos/actions/checkout/commits/<that tag> --jq .sha
```

Send me the output, or enable Bash, and I'll make the edit. The line will look like `uses: actions/checkout@<40-char-sha> # vX.Y.Z`. Alternatively, `pinact run` rewrites the reference and keeps the version comment. It edits files in place, so run it on a clean tree.

I'm pinning to the latest release rather than `v4`, because the skill I'm following says to use the newest release that passes your cooldown. Say so if you want to stay on the v4 line.

The same file has three other problems that I haven't touched, since you only asked about pinning:
- **Script injection:** line 14 puts `${{ github.event.pull_request.title }}` straight into a `run:` block. A pull request title can run commands on the runner. The fix is to pass it through `env:` instead.
- **Permissions:** `permissions: write-all` at workflow level on a `pull_request` trigger gives the job far more access than it needs. I'd use `permissions: {}` at workflow level and `contents: read` on the job.
- **Checkout hardening:** the job has no `timeout-minutes`, and checkout has no `persist-credentials: false`.

Do you want me to fix those when I do the pin?
