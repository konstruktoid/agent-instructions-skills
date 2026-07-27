I found the workflow at `.github/workflows/deploy.yml`, which references `actions/checkout@v4` — the only third-party action in this repo.

I don't have shell or network access in this session (no Bash/curl/gh CLI tool available), so I can't resolve the current commit SHA myself, and the skill explicitly forbids writing a SHA from memory since a wrong or stale one can fail silently or resolve to something unintended.

To pin it correctly, please run:
```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name
gh api repos/actions/checkout/commits/<that-tag> --jq .sha
```
and share the resulting tag and SHA — I'll then update line 13 to `uses: actions/checkout@<sha> # <tag>`.

Two other things I noticed while reading this file that are outside your specific request, so I'm flagging rather than changing them: `permissions: write-all` at workflow level, and the PR title interpolated directly into a `run:` shell command (`${{ github.event.pull_request.title }}`), which is a script-injection risk. Let me know if you'd like those addressed too.
