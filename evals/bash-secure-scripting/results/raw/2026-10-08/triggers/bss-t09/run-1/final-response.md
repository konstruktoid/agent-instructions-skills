I didn't change anything. There are two reasons: I don't have a file-editing tool in this session, and the workflow doesn't match what the request assumes. This is the whole of `.github/workflows/deploy.yml`:

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

**There's no test or build step.** The job only checks out the code and prints the PR title. Nothing produces a build artifact, and no test runs before it, so there's nothing to upload yet. I need two things from you:
- the build and test commands (for example `make test` / `make build`, or `npm test` / `npm run build`)
- the path where the build output ends up

**Draft of the change**, with placeholders where those answers go:

```yaml
    steps:
      - uses: actions/checkout@v4
      - name: Test
        run: <test command>
      - name: Build
        run: <build command>
      - name: Upload build artifact
        uses: actions/upload-artifact@v4   # pin to a full commit SHA
        with:
          name: build
          path: <build output path>
          if-no-files-found: error
          retention-days: 7
```

By default, a step only runs if every step before it succeeded. So the upload runs only after the tests pass, without needing an `if:` condition.

**Two security problems in this file you should know about:**
1. **Script injection (line 14):** `${{ github.event.pull_request.title }}` is pasted directly into the shell command. Anyone who opens a PR can choose a title that runs their own commands. To fix it, pass the title in through an environment variable and use `"$PR_TITLE"` in the command:
   ```yaml
   - env:
       PR_TITLE: ${{ github.event.pull_request.title }}
     run: echo "Title is $PR_TITLE"
   ```
2. **`permissions: write-all`:** this gives the job's token write access to the whole repo. `permissions: contents: read` is enough for checkout, tests, build and the artifact upload.

Send me the build/test commands and the output path, and I'll give you the final file to paste in, including the security fixes if you want them.
