I made the changes. `actionlint` is clean. `zizmor` (pedantic) has 2 low findings left, which I left alone, and nothing has run on a real runner.

**Changes**
- **`actions/setup-toolchain/action.yml`**:
  - There is a new "Lint with ruff" step after the Python and cache steps. It installs ruff from a new `ruff-version` input (default `0.17.2`) and runs `ruff check .`.
  - The cache key is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. I added `runner.os` so Linux and Windows caches don't collide.
  - The final `echo` step passed `inputs.version` straight into the shell script. It now goes through `env:`.
- **`.github/workflows/ci.yml`**: there is a new `test-windows` job on `windows-latest` with the same steps as `test`. I also added a workflow-level `concurrency` group to clear a `zizmor` finding.
- **`README.md`**: the action row now describes the ruff lint and the cache key, and a new CI table lists both jobs.

**Action pins**
- **`actions/setup-python`**: it was `@v5`. It is now pinned to v7.0.0 (`5fda3b9…`). v7.1.0 is the latest release, but it was published two days ago, so I held back to v7.0.0 to stay outside a 7-day cooldown. v7.0.0 removes the `pip-install` input, which this action doesn't use.
- **`actions/cache`**: it was `@v4`. It is now pinned to v6.1.0 (`55cc834…`), the latest release.
- I only read the v7.0.0 notes for `setup-python`, not the intermediate versions' notes or `actions/cache`'s. Both major bumps are worth a look in review.

**Not resolved**
- **`zizmor` self-repository findings:** it suggests `$/actions/setup-toolchain` in place of `./actions/setup-toolchain`. I haven't confirmed that syntax is supported by `actionlint` or the runner, so I left it.
- **Not run on GitHub:** pushing and triggering a run would affect the remote, so I didn't. The Windows job is unproven for three reasons:
  - The `~/.cache/build` cache path.
  - `pip install` in the bash step.
  - Whether `ruff check .` passes on this repo's code.
- **Missing or changed items:**
  - `uv.lock` isn't in the repo. `hashFiles` returns an empty string for a missing file, so the key works but won't change until the lockfile exists.
  - The tests still depend on pytest being available, as before.
  - There is no `dependabot.yml`, so I didn't add one.
