Both files parse cleanly.

One thing to flag: on `windows-latest` the composite action's `runs.using: composite` steps that pin `shell: bash` still work (Git Bash ships on the Windows runner), so no changes were needed there.

Files changed:
- `actions/setup-toolchain/action.yml` — added `ruff` lint step after toolchain install; cache key now includes `hashFiles('**/uv.lock')`.
- `.github/workflows/ci.yml` — new file; single job with `os: [ubuntu-latest, windows-latest]` matrix running the composite action + `pytest`.
- `README.md` — updated action description, added CI platforms table.

No prior CI workflow existed in this repo, so I created one from scratch rather than adding a job to something pre-existing — flagging that assumption in case a workflow was expected to already be here.
