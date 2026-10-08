I haven't changed anything yet, because I can't look up a real commit SHA in this session. I only have file read and search tools here, with no shell or `gh`. The skill says never to write a SHA from memory, since an invented one either fails or points at something unintended.

The workflow `.github/workflows/deploy.yml` has one action to pin, `actions/checkout@v4` on line 13. Please run these two commands, or give me a shell so I can run them:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name
gh api repos/actions/checkout/commits/<that tag> --jq .sha
```

I'd pin the newest release that clears your cooldown, not `v4`, so this may be a major-version bump. I'd note that in the PR description. I'll write the result as `uses: actions/checkout@<sha> # <tag>`.

You could also run `pinact run` on a clean tree, which rewrites every `uses:` line and keeps the version comment. I'd ask you first before running it.

The same file has other problems you didn't ask me to fix. Do you want me to fix them in the same change?
- `permissions: write-all` should be `permissions: {}` at workflow level, with `contents: read` on the job.
- Line 14 puts `${{ github.event.pull_request.title }}` directly in a `run:` block, which allows script injection. The title should go through `env:` instead.
- The checkout step needs `persist-credentials: false`.
- The job needs a `timeout-minutes`.

I'd also run `actionlint` and `zizmor` over the result once the edit is in.
