I made all the changes. `actionlint` passes, but nothing has run on a GitHub runner, and **as the repo stands I expect both test jobs to fail**.

**Changes**
- **Lint step:** the composite action now installs `ruff==0.17.6` (the current PyPI release) and runs `ruff check .` after the toolchain setup.
- **Cache key:** it's now `build-<OS>-<version>-<hash of uv.lock>`. I added the OS so Linux and Windows don't share a key. There are no `restore-keys`, so a lockfile change gives a clean miss.
- **Windows:** a new `test-windows` job mirrors the Linux one, with the same read-only permission, timeout, action and test command. As you asked for a second job, I didn't convert the two into a `strategy.matrix`.
- **README:** I updated the table row.

**Two related fixes in the action**
- `setup-python` and `cache` were referenced by movable tags. I pinned them to the commits for v5.6.0 and v4.3.0, which `v5` and `v4` currently point to, matching how `checkout` is pinned.
- The `echo` step inserted the `version` input directly into the shell script. It now passes it through an environment variable.

**Before you merge**
- **pytest is never installed:** neither the workflow nor the action installs it, and `setup-python` doesn't normally provide it. This was already true of the Linux job.
- **No tests in the repo:** even with pytest installed, it exits with code 5 when it finds none, which fails the job.
- **No `uv.lock` in the repo:** `hashFiles` returns an empty string, so the key won't change with dependencies until a lockfile is committed at the root of the checkout.
- **Lint applies to every caller:** because it's inside the shared action, any lint error stops a job before its tests run.

If these files are only part of your project, the first three may not apply. Otherwise, the next step is to add your tests and `uv.lock`, and install the dependencies, including pytest, before the test step.

`zizmor --offline` also reported two low-severity findings, one per job: it suggests `$/...` instead of `./actions/setup-toolchain`. I left the existing `./` form as it is. Nothing is committed.
