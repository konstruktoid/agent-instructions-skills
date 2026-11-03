I made all four changes. I haven't run any of it, because the workflows only execute on GitHub Actions.

- **Lint step:** `actions/setup-toolchain/action.yml` now installs ruff with pip and runs `ruff check .` after the Python setup and cache steps. It uses `shell: bash`, so it works on both runners.
- **Cache key:** the key is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. A lockfile change invalidates the cache. I also added `runner.os` so Linux and Windows caches don't collide.
- **Windows job:** `.github/workflows/ci.yml` has a new `test-windows` job. It mirrors `test`, with the same checkout, the local action and `python -m pytest`, but on `windows-latest`.
- **README:** the action row describes the new behaviour, and I added a small table listing the two CI jobs.

I also changed the `echo "Installed ${{ inputs.version }}"` step to read the version from an env var instead of interpolating it into the shell script. That closes a script-injection pattern.

- **Unpinned actions:** `setup-python@v5` and `cache@v4` in the composite action are pinned to tags, while checkout is pinned to a SHA. I left them as they were because I couldn't look up the SHAs here.
- **Missing `uv.lock`:** `hashFiles('uv.lock')` returns an empty string if the file is missing. The cache will still work, but it won't invalidate on dependency changes.
