I made all the changes, but **I expect both CI jobs to fail at the test step**, and nothing has run on GitHub yet.

**What you asked for**
- **Lint:** the composite action now installs `ruff==0.17.6` and runs `ruff check` on the caller's checkout.
- **Cache key:** it's now `build-<os>-<version>-<hash of uv.lock>`. I added the OS so the Linux and Windows keys stay distinct.
- **Windows:** there's a new `test-windows` job on `windows-latest` with the same steps as the Linux job. I used a second job, as you described, rather than a `strategy.matrix`.
- **README:** I updated the table row.

**Other changes**
- **Pinned actions:** `setup-python` went from `@v5` to v7.1.0 and `cache` from `@v4` to v6.1.0, both pinned by commit SHA. These major versions need Actions Runner 2.327.1 or later, which matters only if you use self-hosted runners elsewhere. v7 of `setup-python` also removes the `pip-install` input, which this action doesn't use.
- **Script injection:** the `echo` step now reads the version from an environment variable instead of inserting `${{ inputs.version }}` into the script.
- **Concurrency:** a new push to a pull request now cancels the older run, so two jobs don't double the wasted runner time.

**Check these before merging**
- **pytest is never installed:** neither the action nor the workflow installs it, so `python -m pytest` should fail with "No module named pytest". The repo also has no tests, and pytest fails when it collects none. This was already true of the Linux job.
- **No `uv.lock` exists:** the hash is empty until a lockfile is committed at the repository root, so lockfile changes can't invalidate anything yet.
- **Cache contents:** nothing in the repo writes to `~/.cache/build`, so check that your real build does.
- **Lint scope:** every caller of the action now fails if ruff finds a problem.

**Verification**
- **actionlint:** clean.
- **zizmor** (pedantic, offline): two low findings remain, so it isn't fully clean. Both suggest writing `./actions/setup-toolchain` with its newer `$/...` syntax. I kept the existing form and added no suppression.
- **ruff:** version 0.17.6 runs locally and exits 0, but only because there are no Python files to check.
- **Not tested:** the install step, the cache behaviour and the Windows job only get exercised by a real run, such as opening a pull request. I haven't committed or pushed anything.

**Possible follow-ups**
- Install the test dependencies, for example with `uv sync --locked` once you have a `pyproject.toml` and `uv.lock`.
- Add a Dependabot config to keep the action pins current. It won't update the ruff version written in the `run:` step.
