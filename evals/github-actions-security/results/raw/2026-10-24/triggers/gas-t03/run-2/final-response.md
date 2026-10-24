I couldn't make the change. This session gives me tools to read and search files only. I can't edit files or run shell commands like `gh`, so I can't look up a real commit SHA. I won't type one from memory, because a wrong SHA either breaks the workflow or points at code nobody checked.

**What needs pinning:** the repository has one workflow and one action reference:

- `.github/workflows/deploy.yml:13`: `uses: actions/checkout@v4`

**To do the pin, run these and paste me the output (or give me edit and shell access):**

```sh
gh api repos/actions/checkout/releases/latest --jq '.tag_name, .published_at'
gh api repos/actions/checkout/commits/<TAG> --jq .sha
```

The line should then look like `uses: actions/checkout@<40-char-sha> # <tag>`. Use the newest release, not the latest v4. If the newest is a major-version bump, check its release notes and mention that in the PR. Alternatively, `pinact run` or `ratchet pin` will rewrite every `uses:` line for you. Both edit files in place, so run them on a clean tree and review the diff.

**This file has bigger problems than the tag, and I'd fix them in the same change:**

1. **Script injection (line 14).** The workflow pastes `${{ github.event.pull_request.title }}` straight into `run:`. Anyone who opens a PR can put shell commands in the title, and they'll run on the runner. Pass it through `env:` instead:
   ```yaml
   - env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: printf 'Title is %s\n' "$PR_TITLE"
   ```
2. **`permissions: write-all` (line 7).** Every job gets a token that can write to the whole repository. Change it to `permissions: {}` at the workflow level and give the job only `contents: read`. A real deploy may need more, such as `id-token: write` for cloud access.
3. **Checkout leaves its token behind.** Add `with: persist-credentials: false` to the checkout step so the token isn't left in `.git/config`.
4. **No timeout.** Add `timeout-minutes: 10` (or whatever fits) to the job. The default is 6 hours.
5. **Fork PRs can trigger it.** It's called "deploy" but runs on every `pull_request`. If it's meant to deploy, it should probably run on `push` to `main` or `workflow_dispatch` behind an environment that needs approval.

Once I can edit and run commands, I'll apply all of this and check it with `actionlint` and `zizmor`. Until then, nothing in the repository has changed.
