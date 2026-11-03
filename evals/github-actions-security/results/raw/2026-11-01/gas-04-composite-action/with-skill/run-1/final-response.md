I extended the composite action, added the Windows job, and updated the README. I haven't run the workflow on a runner. `actionlint` is clean. `zizmor` (pedantic) reports 2 low-severity findings, both stylistic.

**`actions/setup-toolchain/action.yml`**
- **Ruff step:** after setup-python and the cache restore, it installs `ruff==0.17.3` (the latest release when I checked) and runs `ruff check .`.
- **Cache key:** it is now `build-${{ runner.os }}-<version>-${{ hashFiles('uv.lock') }}`. I added `runner.os` so Linux and Windows caches don't collide.
- **Action pins:** `actions/setup-python` and `actions/cache` were on mutable tags (`@v5`, `@v4`). They are now pinned to commit SHAs for their latest releases, v7.1.0 and v6.1.0. Both are major-version jumps I haven't read the release notes for.
- **Injection fix:** the `echo "Installed ${{ inputs.version }}"` step interpolated an input straight into the shell. It now passes the value through `env:`.

**`.github/workflows/ci.yml`**
- **Windows job:** `test-windows` runs on `windows-latest` with the same checkout, `./actions/setup-toolchain` and `python -m pytest` steps, and the same read-only permissions and timeout as `test`.
- **Concurrency:** I added a workflow-level `concurrency` group because zizmor flagged its absence. It cancels in-progress runs for the same ref.

**README:** the action row now mentions ruff and the cache key, and there is a new CI matrix table listing both jobs.

**Open items**
- **Remaining `zizmor` findings:** it suggests `$/actions/...` instead of `./actions/...` for the local action reference. I left `./` because it's the conventional form. This is an auto-fix you can accept.
- **No `uv.lock`:** the repo has none, so `hashFiles('uv.lock')` is empty and the key effectively ignores the lockfile until you add one.
- **No Python files or tests:** the repo has no Python sources or tests, so `ruff check .` and `pytest` will have nothing to check. `pytest` exits non-zero when it collects no tests.
- **Not run on a runner:** the Windows job and the bash `run` steps are unverified until a pull request triggers them. I didn't push or trigger a run, since that needs your go-ahead.
- **Possible Windows breakage:** `~/.cache/build` and the `pip install` in the bash step are the most likely places to fail.

I changed the files but haven't committed anything.
