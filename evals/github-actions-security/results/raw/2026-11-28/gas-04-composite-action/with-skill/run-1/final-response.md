I made all the changes, but nothing has run on a GitHub runner, and I expect the test step to fail on both platforms.

**What changed**
- **Lint:** the composite action now installs `ruff==0.17.6` and runs `ruff check .` after Python is set up and the cache is restored.
- **Cache key:** it is now `build-<OS>-<version>-<hash of uv.lock>`. I added the OS so Linux and Windows entries stay separate.
- **Windows:** there is a new `test-windows` job with the same steps and permissions. The existing `Test` job keeps its name, so any required status check on it still matches.
- **README:** the table row describes the lint step and the cache key.

**Other changes in files I touched**
- **Action pins:** I replaced the mutable tags with commit SHAs: `setup-python` v5 → v7.1.0 and `cache` v4 → v6.1.0. Both are major upgrades that run on Node 24, so self-hosted runners would need version 2.327.1 or later; your `ubuntu-latest` and `windows-latest` jobs use hosted runners. v7 of `setup-python` also removes the `pip-install` input, which you don't use. I didn't get release notes for the `cache` major versions, so check those before merging.
- **Script injection:** the `echo` step now reads the version from an environment variable instead of pasting `${{ inputs.version }}` into the script.
- **Concurrency:** a new push to a pull request now cancels the previous run.

**Check before merging**
- **pytest is never installed:** neither the workflow nor the action installs it, so `python -m pytest` will probably fail with "No module named pytest". This was already true of the Linux job.
- **No Python project in the repo:** there are no tests, `.py` files or `uv.lock`. Even with pytest installed, it exits with an error when it finds no tests. Until `uv.lock` exists, its part of the cache key is empty. If the lockfile will live in a subdirectory, change the pattern to `**/uv.lock`.
- **Lint applies to every caller:** because ruff is inside the shared action, a lint error stops any job that uses it, and here it runs once per platform. `ruff` is pinned in the `run:` line, so you'll need to bump it by hand.

**Verification**
- `actionlint` passes.
- `zizmor` 1.31.1 still reports two low-severity `self-repository` findings. It suggests `$/actions/setup-toolchain` instead of `./actions/setup-toolchain`, once for the existing job and once for the new one. I kept `./` to match the existing code, because switching changes how the action is located and I couldn't test that. I didn't suppress the findings.
- `zizmor` ran offline, so its online checks were skipped. `gh` isn't logged in, so I looked up the action versions from the public repositories instead.

Nothing is committed or pushed. Opening a pull request would run both jobs and show whether the Windows setup and cache step work. You may also want a Dependabot config for `github-actions`, with a cooldown, so the new pins stay current.
