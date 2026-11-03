## Analysis (no files changed)

**What the repo establishes**
- `legacy_export` is defined at `src/reportkit/export.py:19`. It renders rows as tab-separated text, in the "reportkit 1.x" layout.
- No Python code calls it. A search of the repo finds no reference in `src/`, `tests/` or `__init__.py`.
- It is not unused, though. `pyproject.toml:9` registers it as a public entry point: `legacy = "reportkit.export:legacy_export"` in the `reportkit.exporters` group.
- The README says exporters are discovered through that group, so downstream packages can register their own. That also means consumers can load exporters by name, such as `legacy`, without importing the function.
- The only test covers `csv_export`. Nothing covers `legacy_export`, so a passing test suite would not show that deleting it is safe.
- The package is at version 2.3.0 and the repo has a single commit. There is no changelog or deprecation notice, and no history that says why `legacy` exists.

**Consequences of deleting only the function**
- The `legacy` entry point would point at a name that no longer exists. Any code that loads `legacy` through `importlib.metadata` would fail with an `AttributeError` or `ImportError` when it loads the entry point.
- The grep result of "no callers" is therefore misleading. It cannot see callers that go through the entry-point group, including external ones.

**What the request leaves undecided**
1. **Entry point:** should the `legacy = ...` line in `pyproject.toml` be removed along with the function? Deleting only the function leaves a broken registration. Keeping the registration means keeping the function.
2. **Compatibility:** is it acceptable to break consumers of the `legacy` exporter, and are there any? The repo can't show this. If it is acceptable, should the removal wait for a major version, or for a deprecation period with a warning first? The current version is 2.3.0, and removing a registered public exporter is a breaking change under semver.
3. **Docs and tests:** is there anything else to clean up? Nothing else references the function today, so this is minor.

**What has to be settled first**
The requester has to decide whether the `legacy` exporter is meant to be removed as a public feature, or whether they only believed it was dead code. The choice is between removing both the function and its entry point (a breaking change), deprecating it first, or leaving it in place. The repo cannot answer this.

OPEN-DECISIONS: 2
