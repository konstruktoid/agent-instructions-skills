I've made all three changes and updated the README. `actionlint` passes, but nothing has run on GitHub, so neither job nor the Windows path is verified.

**What you asked for**
- **Lint step:** the composite action now installs `ruff==0.17.6`, the latest release on PyPI, and runs `python -m ruff check .` after setting up Python.
- **Cache key:** it's now `build-<OS>-<version>-<hash of uv.lock>`. I added the OS so the Ubuntu and Windows keys stay distinct.
- **Windows job:** `test-windows` mirrors the Ubuntu job, with the same action, tests, read-only permissions and timeout. I wrote it as a second job, as you described, not as a `strategy.matrix`.
- **README:** I updated the table row.

**Other changes to the action**
- **Pinned actions:** `setup-python` and `cache` are now pinned to commit SHAs (v5.6.0 and v4.3.0, same major versions as before), matching how `ci.yml` pins checkout.
- **Input handling:** the `echo` step now reads `version` through an environment variable instead of inserting it directly into the shell script, which closes a script injection risk.

**Check before merging**
- **No `uv.lock` in the repo:** until one is committed at the root, the hash is an empty string and lockfile changes can't invalidate anything.
- **pytest is probably missing:** neither the action nor the workflow installs it, so `python -m pytest` will likely fail on both platforms. This was already true of the Ubuntu job. There are also no tests in the repo, and pytest exits with an error when it finds none.
- **Lint blocks tests:** because ruff runs inside the shared action, a lint error stops the job before tests, and the lint runs once per platform.
- **Required checks:** if branch protection requires `Test`, add `Test (Windows)` too if it should block merges.

`zizmor` reports two low-severity findings, both suggesting `$/...` instead of `./actions/setup-toolchain` for the local action reference. I left the existing form and used the same one in the new job.

Nothing is committed.
