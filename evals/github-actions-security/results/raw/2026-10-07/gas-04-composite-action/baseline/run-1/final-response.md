I made the three changes and the README update, but none of it has been run, because there's no CI available here.

- **Composite action** (`actions/setup-toolchain/action.yml`):
  - **Lint:** a new step after the Python setup installs ruff and runs `python -m ruff check .`.
  - **Cache key:** it is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. I added `runner.os` so Linux and Windows don't share a cache.
  - **Echo step:** it now passes the version through an `env` variable instead of interpolating it into the shell script, which avoids script injection.
- **CI workflow:** I added a `test-windows` job on `windows-latest`. It has the same checkout, setup action and `pytest` steps as the Linux job, with the same pinned checkout SHA and read-only permissions. I wrote it as a second job rather than a `strategy.matrix`, to keep the Linux job unchanged.
- **README:** the action row now mentions ruff and the cache key, and there's a new Workflows table listing both jobs.

Things you should know:
- **No `uv.lock`:** the repo has none, so `hashFiles('uv.lock')` returns an empty string and the key only changes with OS and version until you add one.
- **Unpinned actions:** inside the composite action, `setup-python@v5` and `cache@v4` are pinned to tags, while the workflow pins by SHA. I left them because I can't look up SHAs here. Pinning them would be worth doing.
- **Unpinned ruff:** `pip install ruff` isn't version-pinned, so lint results can change when ruff releases.
- **Ruff config:** the repo has no ruff config, so ruff runs with its defaults.
