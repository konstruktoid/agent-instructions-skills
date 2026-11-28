I've made all the changes, but **expect both CI jobs to fail as the repository stands**. The existing `python -m pytest` step has nothing installing pytest and there are no tests in the repo. I left that alone, and the Windows job has the same step.

**Changes**
- **Lint step:** the composite action now installs `ruff==0.17.6` and runs `ruff check .` after Python is set up.
- **Cache key:** it's now `build-<os>-<version>-<hash of uv.lock>`. I added the OS so Linux and Windows don't share a key.
- **Windows:** there's a new `test-windows` job on `windows-latest` with the same steps as the Linux job. I used a second job, as you described, rather than a `strategy.matrix`. The Linux job keeps its name, so any required status check on `Test` still matches.
- **README:** I updated the table row.

**Other changes I made along the way**
- **Pinned actions:** both actions inside the composite are now pinned by commit SHA. This is a major version jump: `setup-python` v5 → v7.1.0 and `cache` v4 → v6.1.0. Both now run on Node 24, and v7 of `setup-python` drops the `pip-install` input, which you don't use.
- **Script injection:** `inputs.version` now reaches the `echo` step through an environment variable instead of being pasted into the script.
- **Concurrency:** a new push to a pull request now cancels that PR's older run.

**Verification**
- `actionlint` passes.
- `zizmor` (pedantic, offline) isn't fully clean: it reports two low findings suggesting `$/actions/setup-toolchain` instead of `./actions/setup-toolchain`. I kept the existing `./` form and didn't test the new syntax or suppress the findings.
- The online `zizmor` audits didn't run because there's no GitHub token here.
- I didn't run the workflow or ruff, so the behaviour on both runners is untested. Opening a pull request would exercise it.

**To check before merging**
- **No `uv.lock` yet:** `hashFiles('uv.lock')` returns an empty string until a lockfile is committed at the repository root, so lockfile changes can't invalidate anything yet. If yours lives in a subdirectory, use `'**/uv.lock'`.
- **Test dependencies:** to get CI passing, you need tests and a step that installs pytest, for example through `uv sync` once you have a `pyproject.toml` and lockfile.
- **Lint scope:** because the lint lives in the shared action, any workflow that uses it will now fail on ruff errors, and it needs the code checked out first.
- **Keeping pins current:** the repo has no Dependabot config. If you add one, include `/actions/setup-toolchain` as well as `/`. The `ruff` version is pinned inside a script, so Dependabot won't update it.
