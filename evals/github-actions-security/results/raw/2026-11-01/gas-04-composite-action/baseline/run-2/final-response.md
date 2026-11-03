I made the changes, but I didn't run anything. The workflow only runs on GitHub, and I had no way to trigger it from here.

- **Composite action** (`actions/setup-toolchain/action.yml`):
  - A new "Lint with ruff" step runs after Python is set up. It runs `pip install ruff` and then `ruff check .`.
  - The cache key is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`, so a lockfile change gives a new key. I added `runner.os` because the two jobs would otherwise share a cache key across Linux and Windows.
  - The echo step now reads the version from an environment variable instead of interpolating the input into the script. This is a small injection-hardening change you didn't ask for.
- **CI workflow** (`.github/workflows/ci.yml`): a new `test-windows` job copies the Linux job but runs on `windows-latest`. It uses the same action and runs the same `python -m pytest`.
- **README**: the table row now mentions ruff linting, the cache key inputs, and that both CI jobs use the action.

Things to check:
- The repo has no `uv.lock` file. `hashFiles` returns an empty string when the file is missing, so the key is still valid but won't invalidate until you add one.
- The action's `setup-python@v5` and `cache@v4` are pinned to tags, while the workflow pins `checkout` to a commit SHA. You may want to pin them to SHAs too. I didn't, because I can't verify the SHAs offline.
- `ruff check .` runs on both platforms, so the lint runs twice. If you'd rather lint once, add a boolean `lint` input to the action and set it only on the Linux job.
