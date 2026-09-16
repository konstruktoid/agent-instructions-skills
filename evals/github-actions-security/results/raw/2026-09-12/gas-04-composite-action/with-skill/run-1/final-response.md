Changes made:

- `actions/setup-toolchain/action.yml` — pinned `actions/setup-python` (v7.0.0) and `actions/cache` (v6.1.0) to resolved commit SHAs, added `astral-sh/ruff-action@278981a` (v4.1.0) as a lint step after the toolchain install, added `hashFiles('**/uv.lock')` to the cache key, and fixed a pre-existing template-injection finding on the `echo` step (moved `inputs.version` through `env:`).
- `.github/workflows/ci.yml` — converted the `test` job into a `matrix` over `ubuntu-latest`/`windows-latest` (`fail-fast: false`) rather than a literal second job block, since a matrix is what "covers both platforms" idiomatically and keeps one definition instead of two to drift out of sync — say if you actually wanted two separately named jobs. Also added a `concurrency` group, which zizmor flagged as missing once the job fanned out across a matrix.
- `README.md` — noted ruff linting and the `uv.lock`-keyed cache in the actions table, added a CI matrix table.

Verification: `actionlint` and `zizmor@1.29.0 --persona=pedantic` both clean after one fix cycle. I did not push a branch or trigger the workflow, so the Windows leg and the new cache key are structurally verified but not run — say if you want me to push to a branch to confirm the matrix actually executes on `windows-latest`.
