I made the changes but haven't run them. This environment can't run GitHub Actions, so none of it has been tested on a runner.

**`actions/setup-toolchain/action.yml`**
- **Lint step:** a new step after the Python setup installs ruff and runs `ruff check .`.
- **Cache key:** it is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. A lockfile change invalidates the cache. I added `runner.os` so Linux and Windows caches don't collide.
- **Input handling:** the `echo` step interpolated `${{ inputs.version }}` straight into the shell script. It now passes the value through an `env` variable, which avoids script injection.

**`.github/workflows/ci.yml`**
- I added a `test-windows` job on `windows-latest`. It copies the existing job: same checkout, same action, same `pytest` run, with `contents: read` permissions.

**`README.md`**
- The action's description now mentions the lint step and the new cache key. I also added a CI coverage table listing both jobs.

**Things to check**
- There is no `uv.lock` in the repo. `hashFiles` returns an empty string for a missing file, so the key still works, but it won't invalidate on anything until a lockfile exists.
- `actions/setup-python@v5` and `actions/cache@v4` in the composite action are pinned to tags. The workflow pins `actions/checkout` to a commit SHA. I left the tags alone because I couldn't look up the SHAs here. Pinning them would make the action consistent with the workflow.
- `ruff check .` will fail the job if the repo has lint violations. I didn't add a ruff config.

I haven't committed anything.
