I made all the requested changes. `actionlint` and `zizmor` (pedantic) both come back clean, but I haven't run the workflow on a runner, so the behaviour is unverified. I didn't push anything. A pull request touching the workflow would exercise it, including the Windows job.

**`actions/setup-toolchain/action.yml`**
- **Lint step:** it runs after the toolchain is installed. It does `pip install "ruff==0.16.10"`, then `ruff check .`. I pinned ruff because an unpinned install would be a mutable dependency. It was released six days ago, so it is inside a 7-day cooldown if you hold ruff to the same one.
- **Cache key:** it is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. A lockfile change invalidates it. I added `runner.os` so Linux and Windows don't share a cache entry. The repo has no `uv.lock` yet, so the hash is empty until one is committed.
- **Action pins:** the actions were on mutable tags (`@v5`, `@v4`). They are now pinned by SHA to the latest releases: `setup-python` v7.0.0 and `cache` v6.1.0. Both clear the cooldown.
- **Major-version bumps:** `setup-python` goes from v5 to v7, and its notes mention an ESM migration and removal of the `pip-install` input. `cache` goes from v4 to v6. The workflow uses neither of those changes, but you may want to record them in the PR description.
- **Injection fix:** the `echo "Installed ${{ inputs.version }}"` step interpolated an input straight into a shell script. It now passes the value through `env:`.

**`.github/workflows/ci.yml`**
- The `test` job now uses a matrix over `ubuntu-latest` and `windows-latest`. Each leg runs the same composite action and `python -m pytest`. I set `fail-fast: false` so one platform failing doesn't hide the other.
- I added a workflow-level `concurrency` group because `zizmor` flagged it. It cancels superseded runs of the same ref.

**`README.md`**
- The action's row now describes the lint step and the cache key. I added a short "CI matrix" table with the two platform rows.

The lint and test steps use `shell: bash` or the default shell. Windows runners have Git Bash, so the `shell: bash` steps should work there.
