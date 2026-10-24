I made the changes and checked that both YAML files parse. I haven't run the workflow, so none of it has run on GitHub Actions.

- **Action** (`actions/setup-toolchain/action.yml`):
  - A new last step installs ruff and runs `ruff check .`, after the toolchain and cache steps.
  - The cache key is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`, so a lockfile change invalidates it. I also added `runner.os`, so Linux and Windows caches don't collide.
- **CI** (`.github/workflows/ci.yml`): a `test-windows` job copies the Linux job with `runs-on: windows-latest`. It uses the same pinned checkout, the same action and `python -m pytest`.
- **README:** the table row now describes the ruff lint and the cache key.

**Unrequested issues I left alone:**
- The composite action's `setup-python@v5` and `cache@v4` are pinned to tags, not commit SHAs like the workflow's checkout.
- The existing `echo "Installed ${{ inputs.version }}"` step interpolates an input straight into the shell script.
- The repo has no `uv.lock`, so `hashFiles` returns an empty string and the key won't change until one is added.

I can fix the first two if you want.
