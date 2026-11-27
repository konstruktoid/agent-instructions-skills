I made all the changes, but **CI will probably fail as the repo stands, and nothing has run on GitHub yet.**

**What you asked for**
- **Lint step:** `actions/setup-toolchain` now installs `ruff==0.17.6` and runs `ruff check .` after Python is set up. Every caller of the action now gets linted.
- **Cache key:** it's now `build-<os>-<arch>-<version>-<hash of uv.lock>`. I added OS and architecture so the two platforms have clearly separate caches. There are no `restore-keys`, so a lockfile change can't fall back to an old cache.
- **Windows:** there's a new `test-windows` job with the same steps as `test`. I added it as a second job, as you described, rather than using `strategy.matrix`. The Linux job's name is unchanged.
- **README:** the table now describes the new behaviour and lists both platforms.

**Other changes in the files I edited**
- **Action versions:** I pinned them to commit SHAs and upgraded `setup-python` from v5 to v7.1.0 and `cache` from v4 to v6.1.0. Both now run on Node 24, so any self-hosted runner using this action needs version 2.327.1 or later. `setup-python` v7 also removes the `pip-install` input, which you don't use.
- **Version input:** the `echo` step now reads it from an environment variable instead of inserting it directly into the shell script.
- **Concurrency:** a new push to a pull request now cancels the older CI run.

**Fix before relying on CI**
- **No `uv.lock`:** the repo doesn't have one, so that part of the cache key is currently empty and invalidates nothing. It will work once a `uv.lock` is committed at the root.
- **pytest:** neither the workflow nor the action installs it, so `python -m pytest` will likely fail on both platforms. This was already true of the Linux job.
- **No tests:** I found no test files or Python code. Even with pytest installed, it exits with code 5 when it collects no tests, which fails the job.

**Checks**
- `actionlint` passes.
- `ruff` 0.17.6 runs locally on Linux but finds no Python files to check.
- `zizmor` (pedantic, offline) still reports two low-severity `self-repository` findings. It wants `uses: ./actions/setup-toolchain` written as `$/actions/setup-toolchain`, once per job. I left them because its automatic fix is marked unsafe and I couldn't test the new syntax on a runner.
- The Windows job, the cache behaviour and the upgraded actions remain untested until a pull request runs them.

**Worth considering**
- There's no Dependabot config, so the pinned SHAs won't update by themselves. The `ruff` version is written inside a script, so you'd need to bump it by hand either way.
- If you require status checks before merging, add `Test (Windows)` to the list.
