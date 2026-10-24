I made all the changes. actionlint is clean. zizmor's pedantic persona still reports 2 low-severity findings, and I haven't run the workflow.

**Composite action (`actions/setup-toolchain/action.yml`)**
- **Lint step:** a `Lint with ruff` step runs right after `setup-python`. It pins `ruff==0.17.1` (not 0.17.2, which was two days old) and runs `ruff check .`.
- **Cache key:** it is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. I added `runner.os` so the Linux and Windows jobs don't share a cache entry.
- **Pinning:** `setup-python` and `cache` were pinned to tags, so I pinned them to commit SHAs I looked up.
  - `cache` is v6.1.0, the latest release.
  - `setup-python` is v7.0.0, not the latest v7.1.0, which was only two days old. There's a comment on the line saying so.
- **Injection fix:** the `echo "Installed ${{ inputs.version }}"` step interpolated an input straight into the shell script. It now passes the value through `env:`.

**CI workflow (`.github/workflows/ci.yml`)**
- **Windows job:** I added a `test-windows` job on `windows-latest` that runs the same action and `python -m pytest`, with the same permissions and timeout as the Linux job. It's a separate job, as you asked, rather than an OS matrix.
- **Concurrency:** I added a workflow-level `concurrency` group, which zizmor flagged as missing.

**README**
- The action row now mentions ruff and the cache key.
- I added a Workflows table listing both jobs.

**Checks**
- **zizmor:** the 2 remaining findings are its suggestion to write `./actions/...` as `$/actions/...`. That's only a style hint and its auto-fix is marked unsafe, so I left it.
- **Not run:** I did not push or trigger the workflow, so the Windows job is unverified until a pull request runs it. `hashFiles('uv.lock')` also gives an empty hash if the repo has no `uv.lock`. There's no lockfile in the repo now, so the cache key won't change until one is added.

I made no commits.
