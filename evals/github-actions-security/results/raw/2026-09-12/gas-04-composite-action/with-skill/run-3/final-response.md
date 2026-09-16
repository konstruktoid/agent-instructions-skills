Both checks are clean. This is a structural change (no workflow run available in this sandbox to exercise the windows-latest job or the new lint step against a real `uv.lock`), so I'm not claiming behavioral verification beyond static analysis.

Files changed:
- `actions/setup-toolchain/action.yml`: pinned `setup-python`/`cache` to resolved SHAs (v7.0.0, v6.1.0), cache key now includes `hashFiles('**/uv.lock')`, added ruff install + lint steps, fixed a pre-existing template-injection finding on the version-echo step.
- `.github/workflows/ci.yml`: added `test-windows` job (windows-latest) mirroring `test`, added workflow-level `concurrency` block (zizmor flagged its absence once two jobs existed).
- `README.md`: updated action table, added CI matrix table.

Unresolved/deferred: no `uv.lock` exists in this repo yet, so the cache key's hash component is currently empty — harmless but worth flagging since the task implies one should exist.

Task complete — recommend `/clear` before starting unrelated work.
