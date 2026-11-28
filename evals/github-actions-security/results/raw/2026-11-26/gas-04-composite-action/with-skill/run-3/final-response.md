I made all the changes, but **I expect both CI jobs to fail at the test step**. Nothing in the workflow or the action installs `pytest`, and `setup-python` doesn't include it. The repo also has no tests, `pyproject.toml` or `uv.lock`. The Linux job already had this problem, and the Windows job copies it. If these files live elsewhere or are still to come, add an install step for your dependencies.

**What changed**
- **Lint step:** the composite action now installs `ruff==0.17.6` after Python is set up and runs `ruff check .`. Because it's inside the action, a lint error stops the job before tests run, in every workflow that uses it.
- **Cache key:** it's now `build-<OS>-<version>-<hash of uv.lock>`. I added the OS so Linux and Windows don't share a key name. Until a `uv.lock` exists at the repo root, the hash part is empty and nothing gets invalidated.
- **Windows:** there's a new `test-windows` job on `windows-latest` with the same steps. The Linux job keeps its name, so any required status check still matches.
- **README:** I updated the table row.

**Other changes in the same files**
- **Pinned actions:** `setup-python@v5` is now v7.1.0 and `cache@v4` is now v6.1.0, both pinned by commit SHA. These are major upgrades that run on Node 24 (runner 2.327.1 or later). `setup-python` v7 also removes the `pip-install` input, which you weren't using.
- **Script injection:** the version input now reaches the `echo` step through an environment variable instead of being pasted into the script.
- **Concurrency:** a new push to a pull request now cancels the older run.

**Checks**
- **`actionlint`:** passes.
- **`ruff` 0.17.6:** exits cleanly here, but only because there are no Python files to check.
- **`zizmor` (offline, so its online checks didn't run):** two low-severity findings remain, one per job. It suggests writing `./actions/setup-toolchain` with the newer `$/...` syntax. I kept your existing form and didn't suppress the findings.
- **Not run on GitHub:** nothing was committed or pushed, so the Windows job, the cache key and the lint step are untested on a runner. Opening a pull request will exercise them.
- **Release lookup:** `gh` wasn't logged in, so I got versions and commit SHAs from GitHub's public tags and release pages.

**Worth doing next:** add a Dependabot config for `github-actions` with a cooldown so the pins stay current. It won't update the `ruff` version written in the script, so you'd bump that by hand or move it into your project's dependencies.
