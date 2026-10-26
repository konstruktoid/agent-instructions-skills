**Analysis only. I changed no files.**

**What the repo establishes**
- `legacy_export` is defined at `src/reportkit/export.py:19`. It renders rows as tab-separated text, in the "reportkit 1.x" layout.
- A grep for the name finds no Python caller, import or test. `tests/test_export.py` only covers `csv_export`. By static reference, the function looks unused.
- The function is still registered as a public entry point: `pyproject.toml:9` has `legacy = "reportkit.export:legacy_export"` in the `reportkit.exporters` group.
- `exporter(name)` in the same file looks exporters up through that group, and the README says downstream packages discover exporters this way. So `exporter("legacy")` resolves to this function at runtime. Callers that pass the name from config or the CLI would never show up in a grep for `legacy_export`.
- The package is at version 2.3.0, and the function exists to keep 1.x-compatible output. That suggests it was kept on purpose for people migrating from 1.x.
- If the function is deleted and the entry point stays, `exporter("legacy")` fails on `entry.load()` with an `AttributeError`. This would only show up after the package is reinstalled, because installed metadata would go on advertising the entry point until then.
- If the function is deleted and the entry point is removed too, `exporter("legacy")` fails on the tuple unpack with a `ValueError`, because no entry is found. This is also a breaking change for any consumer who uses it.

**What the request leaves undecided**
1. **Is the function really unused?** "Unused" holds inside this repo. The repo can't show whether outside consumers select `legacy` by name. The requester has to confirm this or accept the risk.
2. **What happens to the `legacy` entry point in `pyproject.toml`?** The request names only the function. Removing it alone leaves a broken registration, so the entry-point line has to go as well. That widens the change beyond what was asked, and the requester has to approve it.
3. **Is removing a public exporter acceptable in a 2.x release?** Removing it could break downstream users in a minor or patch release. The requester has to say whether to do it now, deprecate it first (for example with a warning), or wait for a major version bump.
4. **Are other artifacts affected?** No changelog, docs or tests mention `legacy`. The requester should say whether a changelog or version note is wanted.

**What has to be settled first**
Decisions 1 to 3 have to be settled before implementation, and they are all about the `legacy` entry point. Decision 4 is minor and could be settled during implementation.

OPEN-DECISIONS: 3
