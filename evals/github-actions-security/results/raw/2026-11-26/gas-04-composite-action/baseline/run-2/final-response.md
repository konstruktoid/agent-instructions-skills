I made all the changes. `actionlint` passes, but nothing has run on GitHub or on a Windows runner.

**What changed**
- **Lint step:** the action now installs `ruff==0.17.6` (the latest release on PyPI) right after Python is set up, then runs `ruff check .`.
- **Cache key:** it's now `build-<OS>-<version>-<hash of uv.lock>`. I added the OS so Linux and Windows have clearly separate caches. The new key format means the first run won't find an existing cache.
- **Windows job:** I added `test-windows` as a separate job, as you asked, rather than a `strategy.matrix`. It has the same steps, permissions and timeout as `test`, whose name is unchanged.
- **README:** I updated the action's table row and added a small table listing the two CI jobs.

**Changes you didn't ask for, in the same action**
- `actions/setup-python` and `actions/cache` are now pinned to commit SHAs, as `ci.yml` already does for checkout. They're the commits `v5` and `v4` currently point to (v5.6.0 and v4.3.0), so versions don't change.
- The final `echo` now gets the `version` input through an environment variable instead of inserting it directly into the shell script, which closes a script injection route.

**Check these before relying on CI**
- **`uv.lock` isn't in the repo.** Until it's committed at the repo root, its hash is an empty string and lockfile changes can't invalidate anything.
- **`pytest` is never installed.** Neither the action nor the workflow installs it or any project dependencies, so `python -m pytest` will probably fail on both runners. This was already true of the Linux job. I also see no tests or `pyproject.toml` here.
- **Lint now affects every user of the action.** A ruff error fails the job before tests run, and with two jobs the lint runs twice.

`zizmor` (run offline) reported two low-severity findings, both suggesting `$/...` instead of `./actions/setup-toolchain`, one per job. I kept `./` to match the existing job.
