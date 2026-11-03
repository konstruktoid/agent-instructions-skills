## Analysis (no files changed)

**What the repository establishes**
- `legacy_export` is defined at `src/reportkit/export.py:19`. It renders rows as tab-separated text, in the "reportkit 1.x" layout.
- Nothing in the repo calls it by name. A search finds only the definition and one other reference. The tests cover only `csv_export`.
- **It is not unused.** `pyproject.toml:9` registers it as the entry point `legacy = "reportkit.export:legacy_export"` in the `reportkit.exporters` group.
- `exporter(name)` in the same file loads exporters from that group by name. So `exporter("legacy")` resolves to this function today.
- The README says exporters are discovered through entry points so downstream packages can register their own. Callers outside this repo may therefore use `exporter("legacy")`. A search of this repo can't show whether any do.
- The package is at version 2.3.0. The function exists to keep the 1.x output format, so it looks like a compatibility feature.

**What happens if only the function is deleted**
- The `legacy` entry point still names the missing function.
- `exporter("legacy")` would then fail with an `AttributeError` or `ImportError` when it loads the entry point. Nothing would flag this ahead of time, because the tests don't cover it.

**What the request leaves undecided**
1. **Remove the entry point too, or keep the function?** The request treats the function as unused, but the entry point makes it reachable. Deleting the function alone breaks `exporter("legacy")`. Deleting the function and the `pyproject.toml` line removes a public exporter name. Only the requester can say which they intend.
2. **Compatibility policy.** Removing a registered exporter is a breaking change for anyone who selects it by name. In a 2.x release that normally calls for a deprecation period or a major-version bump. Whether to deprecate first, warn, or remove outright is the requester's decision.
3. **Evidence of non-use.** The requester may know that nothing outside this repo uses `legacy`. I can't verify that from here.

**What has to be settled first**
- Whether the `legacy` entry point should be removed together with the function (and whether that removal needs a deprecation step or a version bump).

If the answer is "remove both, no deprecation", the implementation is small: delete the function and the `pyproject.toml` line, and optionally add a test that `legacy` is no longer registered.

OPEN-DECISIONS: 2
