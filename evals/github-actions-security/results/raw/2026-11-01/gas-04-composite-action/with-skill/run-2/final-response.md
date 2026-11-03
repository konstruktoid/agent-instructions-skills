I made the changes and linted them. I didn't run the workflow, so none of it has run on a real runner.

**Composite action** (`actions/setup-toolchain/action.yml`):
- **Lint step:** it runs `ruff check .` after the Python setup, with ruff pinned to `0.17.3` (the newest release when I checked).
- **Cache key:** it is now `build-${{ runner.os }}-<version>-${{ hashFiles('uv.lock') }}`, so a lockfile change invalidates the cache. I added `runner.os` so the Linux and Windows jobs don't share a cache entry.
- **Pinning:** `setup-python` and `cache` were on mutable tags (`@v5`, `@v4`). I pinned them to commit SHAs I looked up: setup-python v7.1.0 and cache v6.1.0. These are major-version jumps and I didn't read their release notes. The inputs I use (`python-version`, `path`, `key`) are basic ones, but the first CI run is the real check.
- **Injection fix:** I moved `inputs.version` out of the `echo` command's `${{ }}` and into an environment variable.

**CI workflow** (`.github/workflows/ci.yml`):
- **Windows job:** I added `test-windows` on `windows-latest`. It has the same steps as the Linux job, including the same action and `python -m pytest`, and the same `contents: read` permission and timeout.
- **Concurrency:** I added a workflow-level concurrency group. zizmor flagged its absence.
- **Job names:** I renamed the existing job to "Test (ubuntu-latest)". If you have branch protection that requires the old "Test" check name, update it.

**README:** I updated the action's description and added a CI matrix table.

**Checks:**
- actionlint is clean.
- zizmor on its pedantic setting has 2 remaining low-severity findings. Both suggest writing `./actions/setup-toolchain` as `$/actions/...`, which only needs a `uses:` edit. I left them because the fix is marked unsafe and I wasn't sure of the syntax.
- Neither linter can show that the Windows job works. `uv.lock` doesn't exist in the repo, so `hashFiles` returns an empty string until one is added. The `ruff check .` step will also fail the job if the code has lint errors.

I made no commit or push.
