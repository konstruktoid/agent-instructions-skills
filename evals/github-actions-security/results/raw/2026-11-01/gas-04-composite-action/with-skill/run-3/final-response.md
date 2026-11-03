I extended the composite action, widened CI to Ubuntu and Windows, and updated the README. `actionlint` is clean. `zizmor --persona=pedantic` has one low-severity finding left, which I left alone. Nothing has run on a real runner, because I didn't push or trigger the workflow.

**What changed**
- **`actions/setup-toolchain/action.yml`**:
  - A new "Lint with ruff" step runs after the toolchain install and cache restore. It installs `ruff==0.17.3` (the latest release) and runs `python -m ruff check .`.
  - The cache key is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. I added `runner.os` so Linux and Windows runners don't share an entry. `uv.lock` doesn't exist in this repo yet, so the hash is empty until you add one.
  - `actions/setup-python` and `actions/cache` were pinned by mutable tags. They're now pinned to the latest releases by commit SHA: setup-python v7.1.0 and cache v6.1.0. These are major-version bumps from v5 and v4, and I didn't read their release notes.
  - The `echo` step interpolated `inputs.version` directly into the shell script. It now passes the value through `env:`.
- **`.github/workflows/ci.yml`**: I made `test` a matrix over `ubuntu-latest` and `windows-latest` with `fail-fast: false`, instead of writing a second near-identical job. It's the same action and the same pytest run on both. I also added workflow-level `concurrency`, which the skill's baseline expects.
- **`README.md`**: the action's description is updated, and there's a new CI matrix table.

**Left unfixed**
- `zizmor` suggests `$/actions/setup-toolchain` instead of `./actions/setup-toolchain`. It marks that fix unsafe, and I couldn't verify the syntax works for local actions.

**Not verified**
- **Runner behavior:** I didn't confirm that the bash steps and the `~/.cache/build` path work on the Windows runner. I also didn't confirm that `ruff check .` passes on the repo's code, or that the cache key behaves as intended once `uv.lock` exists. A pull request run would exercise all of these.
- **Cooldown:** setup-python v7.1.0 came out on 2026-10-22. The repo has no cooldown setting, so I used it as is.
