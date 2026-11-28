I've added the ruff lint step and the `uv.lock` hash to the composite action, added the Windows job and updated the README table. Nothing has run on a GitHub runner, and **I expect both jobs to fail at the test step as the repo stands**.

**Changes**
- **Lint:** the action installs `ruff==0.17.6` with pip after Python is set up, then runs `ruff check .`.
- **Cache key:** it's now `build-<os>-<version>-<hash of uv.lock>`. I added the OS so Linux and Windows have separate entries. Existing cache entries won't match the new key.
- **Windows:** a second job, `test-windows`, runs the same steps on `windows-latest`. I left the `test` job's name alone so any required status check still matches. A single job with an OS matrix would avoid the duplication, but it would change the check names.
- **README:** the table now describes linting and the cache key, and has a new "Tested on" column.

**Other changes in the action**
- **Pinned actions:** `setup-python` went from `@v5` to v7.1.0 and `cache` from `@v4` to v6.1.0, both pinned to commit SHAs that match their release tags. These are major version jumps. Newer versions run on Node 24, so self-hosted users of this action need a recent runner. `setup-python` v7 also removed the `pip-install` input, which this action doesn't use.
- **Version input:** it now reaches the `echo` step through an environment variable instead of being pasted into the script.

**Check before merging**
- **pytest is never installed:** neither the workflow nor the action installs it, so `python -m pytest` should fail with "No module named pytest". This was already true of the Linux job. I also found no tests, and pytest fails when it collects none.
- **There is no `uv.lock`:** the repo only has the workflow, the action and the README. Until a lockfile exists in the caller's checkout, the hash part of the key is empty and nothing gets invalidated.
- **Lint affects every caller:** anyone using this shared action will now fail if ruff finds problems.

**Verification**
- `actionlint` passed.
- `zizmor` 1.31.1 (pedantic, offline, so checks that need the GitHub API didn't run) reported three low findings, so it isn't clean. I stopped after one pass and left them, since fixing them goes beyond what you asked:
  - The workflow has no `concurrency` setting. This is worth adding now that each pull request also uses a Windows runner.
  - Two findings suggest writing `./actions/setup-toolchain` with GitHub's newer `$/` syntax, once for each job.

Opening a pull request would exercise both jobs. The repo also has no Dependabot config, so the new pins won't update on their own. If you add one, include `/actions/setup-toolchain` as well as `/`. Nothing is committed.
