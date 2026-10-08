I made all the requested changes, and `actionlint` and `zizmor` (pedantic) both come back clean. The workflow has not run on a runner, and nothing is committed or pushed.

**`actions/setup-toolchain/action.yml`**
- **Lint step:** it runs after the toolchain and cache steps. It installs `ruff==0.16.9` with pip and runs `ruff check .`. I picked 0.16.9 because 0.16.10 is only 6 days old, which is inside a 7-day cooldown.
- **Cache key:** it is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('**/uv.lock') }}`. I added `runner.os` so Linux and Windows caches don't collide. If a repo has no `uv.lock`, the hash is empty and the key won't change.
- **Pinning:** `actions/setup-python` and `actions/cache` were on mutable tags. They are now pinned to SHAs I looked up: setup-python v7.0.0 and cache v6.1.0, both the latest releases and past the cooldown. I did not read their release notes for breaking changes, and both are major-version jumps from the old `@v5` and `@v4` tags.
- **Template injection:** zizmor flagged `${{ inputs.version }}` inside the `echo` run block. I now pass it through `env:` instead.

**`.github/workflows/ci.yml`**
- **Matrix:** the `test` job runs on `[ubuntu-latest, windows-latest]` with `fail-fast: false`. I used a matrix rather than a second copy of the job, so both platforms run the same action and `pytest` step.
- **Concurrency:** I added a workflow-level concurrency group, which zizmor's pedantic persona asked for.

**README:** the action row now describes the lint step and the cache key, and there is a new "CI matrix" table covering both runners.

**Untested:**
- **Runner behaviour:** I haven't run the workflow, so how `~/.cache/build` and `ruff check .` behave on the Windows runner is unconfirmed. Running it needs a push, which I didn't do without your go-ahead.
- **Ruff config:** if the repo has no ruff config, ruff's default rules apply, and existing code may fail them.
- **Dependabot:** `.github/dependabot.yml` doesn't exist. I'd suggest adding one for `github-actions` with a 7-day cooldown so the pins don't go stale. I left it out because you didn't ask for it.
