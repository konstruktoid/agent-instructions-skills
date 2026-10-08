I've made all four changes, and `actionlint` and `zizmor` (pedantic) both pass. I haven't run the workflow on a runner. The Windows job and the new ruff step are untested, and there's no `uv.lock` in the repo yet, so the key hashes an empty value until one is committed.

- **Composite action (`actions/setup-toolchain/action.yml`):**
  - A new step installs `ruff==0.16.9` after the toolchain setup and runs `ruff check .`. I chose 0.16.9 because 0.16.10 is only 6 days old, inside the 7-day cooldown. I left a comment on the line saying so.
  - The cache key is now `build-${{ runner.os }}-${{ inputs.version }}-${{ hashFiles('uv.lock') }}`. I added `runner.os` so Linux and Windows caches don't collide.
  - The two actions were on mutable tags. I pinned them to commit SHAs: `actions/setup-python` v7.0.0 and `actions/cache` v6.1.0.
- **CI workflow (`ci.yml`):** I added a `test-windows` job on `windows-latest`. It has the same permissions, timeout, checkout and test steps as the existing job.
- **README:** The action row now describes the cache key and the lint step, and there's a new CI matrix table listing both jobs.

I fixed two things that `zizmor` flagged:
- The existing `echo "Installed ${{ inputs.version }}"` step put an input straight into a shell script. It now goes through an environment variable.
- I added a workflow-level `concurrency` group to `ci.yml`.

The major-version jumps on `actions/setup-python` (v5 to v7) and `actions/cache` (v4 to v6) were not checked against release notes, so look at those before merging.

I haven't pushed anything.
