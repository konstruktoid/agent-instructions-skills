I made all the changes. `actionlint` passes and the YAML parses, but nothing has run on GitHub or on a Windows runner, and I haven't committed anything.

**What you asked for**
- **Lint step:** the composite action now installs `ruff==0.17.6` (the current PyPI release) and runs `ruff check` after the Python setup.
- **Cache key:** it's now `build-<OS>-<version>-<hash of **/uv.lock>`. I added the OS so Linux and Windows don't share a key. The first run after merging will miss the cache.
- **Windows job:** `test-windows` mirrors the Linux job's steps, permissions and timeout. The `test` job is unchanged, so a required check named `Test` still matches.
- **README:** the table row describes the new behaviour and has a new column listing both platforms.

**Two hardening changes you didn't ask for**
- `setup-python` and `cache` are now pinned to commit SHAs, as `checkout` already was. They stay on the same major versions (v5.6.0 and v4.3.0).
- The existing `echo` step now receives `version` through an environment variable instead of inserting it directly into the shell script, which could allow script injection if a caller passed untrusted input.

**Check before merging**
- **Tests will likely fail on both platforms:** nothing in the workflow or action installs `pytest`, and the repository has no tests. If `pytest` were installed, finding no tests would still fail the step (exit code 5). The Linux job already had this problem. If your tests and dependencies live elsewhere, add an install step.
- **No `uv.lock` yet:** the repository doesn't contain one, so the hash part of the key is empty until you add it.
- **Lint affects every caller:** any workflow that uses this shared action will now fail on ruff violations.

`zizmor` reports two low-severity style findings, suggesting `$/...` instead of `./...` for the local action reference. One is on the existing line and one on its copy in the Windows job. I left both as they were.

You asked for a second job, so the two jobs are duplicates apart from name and runner. A single job with `strategy.matrix.os` would avoid that, but it would change the check names. I can switch it if you like.
