I made all four changes, but none of it has been run. Nothing was validated locally or on a runner.

- **Lint step** (`actions/setup-toolchain/action.yml`): after the existing steps, it runs `python -m pip install ruff` and then `ruff check .`. It uses `shell: bash`, so it works on Windows too.
- **Cache key**: now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`, so a lockfile change invalidates the cache. I also added `runner.os` so the Linux and Windows caches don't collide.
- **Windows job** (`.github/workflows/ci.yml`): a new `test-windows` job on `windows-latest`. It copies the `test` job: same checkout, same action with version 3.13, same `python -m pytest`, same permissions and timeout. I wrote it as a second job, as you asked, rather than a `matrix:` block.
- **README**: the action's table row now mentions the OS, version and `uv.lock` cache key, and the ruff lint.

- **Missing `uv.lock`:** the repo has no `uv.lock`, so `hashFiles` returns an empty string and the key ends in a trailing `-` until one exists.
- **Lint failures:** `ruff check .` runs with default rules and will fail the job on any finding. There's no ruff config in the repo.
- **Unpinned actions:** `actions/setup-python@v5` and `actions/cache@v4` in the composite action are pinned to tags, while the workflow pins checkout to a SHA. I left them as they were, since looking up SHAs needs network access. You may want to pin them.
