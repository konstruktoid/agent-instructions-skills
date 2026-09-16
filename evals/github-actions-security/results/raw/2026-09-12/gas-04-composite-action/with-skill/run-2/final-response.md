Changed files: `actions/setup-toolchain/action.yml`, `.github/workflows/ci.yml`, `README.md`.

Summary:
- `action.yml`: pinned `setup-python`, `cache` to resolved SHAs (previously floating `@v5`/`@v4`), added `astral-sh/ruff-action@v4.1.0` after toolchain install, added `hashFiles('**/uv.lock')` to the cache key, and fixed a pre-existing template-injection finding (`${{ inputs.version }}` interpolated directly into a `run:` block) by routing it through `env:`.
- `ci.yml`: added `test-windows` job (`windows-latest`) mirroring `test`, renamed both job display names for clarity, and added a `concurrency` block that was missing (zizmor `concurrency-limits` finding).
- `README.md`: updated the actions table and added a CI platform table.

`actionlint` and `zizmor --persona=pedantic` both ran clean (attempt 2 of the bounded loop; attempt 1 surfaced the two pre-existing findings above, now fixed). The workflow itself has not been pushed or triggered — say the word if you want it run on a branch.

I did not stage or commit anything. `/clear` before starting anything unrelated.
