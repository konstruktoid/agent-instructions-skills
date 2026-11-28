I added the ruff lint step, put the `uv.lock` hash in the cache key, added a `test-windows` job and updated the README table. `actionlint` passes and both YAML files parse. I haven't run the workflow itself, on either Linux or Windows.

**What you asked for**
- **Lint:** the action now installs `ruff==0.17.6` (the latest on PyPI, pinned so a new release can't break CI unexpectedly) and runs `ruff check .` after the toolchain setup.
- **Cache key:** it's now `build-<os>-<version>-<hash of uv.lock>`. I also added the OS so the Linux and Windows caches have distinct keys. The new key format means the first run won't find a cache.
- **Windows:** `test-windows` is a separate job, as you described, with the same permissions, timeout, checkout settings, action and test command as the Linux job. If you'd rather have one job with `strategy.matrix.os`, that would remove the duplication.
- **README:** the table row describes the new behaviour, and a new column lists the CI platforms.

**Two other changes to the action**
- **Pinned actions:** `setup-python` and `cache` are now pinned to commit SHAs, matching how the workflow pins `checkout`. They're the commits `v5` and `v4` point to today (v5.6.0 and v4.3.0), so versions don't change, but future updates won't arrive automatically.
- **Version input:** the `echo` step now reads it from an environment variable instead of inserting it directly into the shell script, which prevents script injection if a caller ever passes untrusted text.

**Check these before merging**
- **No `uv.lock` in the repo:** `hashFiles` returns an empty string for a missing file, so the key won't change with dependencies until a lockfile is committed at the root.
- **pytest is never installed:** neither the action nor the workflow installs it, so I expect `python -m pytest` to fail on both jobs. This was already true of the Linux job. There are also no tests or `pyproject.toml` in the repo. If the real project uses uv, adding a dependency install step such as `uv sync` would be the fix.
- **Lint applies to every caller:** because ruff runs inside the shared action, any workflow that uses it will now fail on lint errors, and CI lints once per platform.

Nothing is committed; the changes are in your working tree.
