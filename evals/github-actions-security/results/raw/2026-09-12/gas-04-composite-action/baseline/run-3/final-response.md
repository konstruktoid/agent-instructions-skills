Changes made, YAML validated:

- `actions/setup-toolchain/action.yml` — cache key now includes `hashFiles('**/uv.lock')`; added a ruff lint step after the toolchain install.
- `.github/workflows/ci.yml` — added `test-windows` job (`windows-latest`) running the same action and `pytest` suite.
- `README.md` — updated the actions table and added a CI matrix table.

No `uv.lock` exists in this repo, so `hashFiles` will currently resolve to an empty string — the cache key still changes correctly once a lockfile is added, but verify that's the intended layout before relying on it.

Not committing per your instructions. Let me know if you want a commit.
