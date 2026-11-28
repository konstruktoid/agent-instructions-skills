I added the ruff step, the `uv.lock` hash in the cache key, a `test-windows` job and the README table update. `actionlint` passes and the action YAML parses. Nothing has run on GitHub, so neither the Linux nor the Windows path is tested.

**What you asked for**
- **Lint:** the action now installs `ruff==0.17.6` (the latest on PyPI, pinned) and runs `ruff check .` after the toolchain is set up.
- **Cache key:** it's now `build-<os>-<version>-<hash of uv.lock>`. I added the OS so Linux and Windows keep separate keys.
- **Windows:** `test-windows` is a copy of the Linux job running on `windows-latest`. I added it as a second job, as you described, rather than a `strategy.matrix`. A matrix would remove the duplication if you'd prefer that.
- **README:** the table row now mentions the cache key and linting.

**Two changes you didn't ask for, both in the composite action**
- **Pinned actions:** `setup-python` and `cache` used movable tags, so I pinned them to the commits those tags point to now (v5.6.0 and v4.3.0), matching how `ci.yml` pins checkout.
- **Input handling:** the `echo` step pasted `inputs.version` straight into the shell script, which allows script injection if a caller ever passes untrusted text. It now goes through an environment variable.

**Likely to fail or surprise you on the first run**
- **pytest:** nothing in the workflow or action installs it, so `python -m pytest` will probably fail with "No module named pytest". This was already true of the Linux job.
- **No project files:** the repo as it stands has no tests, Python files or `uv.lock`. pytest exits with an error when it finds no tests. Without a lockfile the hash is just empty, so changes can't invalidate the cache until one is committed.
- **Lint scope:** because ruff is inside the shared action, every workflow that uses it will now fail on lint errors.

`zizmor` still reports two low-severity findings, both suggesting a different syntax for the `./actions/setup-toolchain` reference (one per job). I kept the existing `./` form.

Nothing is committed.
