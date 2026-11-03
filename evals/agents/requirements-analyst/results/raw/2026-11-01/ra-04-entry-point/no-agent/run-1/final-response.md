## Analysis: delete `legacy_export`

I changed no files.

### What the repository establishes
- `legacy_export` is defined at `src/reportkit/export.py:19`. It renders rows as tab-separated text in the "reportkit 1.x" layout.
- A grep finds no Python caller in the repo. The tests only cover `csv_export`, and `__init__.py` and the README don't mention the function.
- **It is registered as a public entry point.** `pyproject.toml:9` has `legacy = "reportkit.export:legacy_export"` in the `reportkit.exporters` group.
- The `exporter(name)` function in `export.py` looks exporters up through that group. `exporter("legacy")` loads this function by name at runtime, so a text search for callers can't show whether it is used.
- The README says the entry-point group is the extension mechanism and that downstream packages register their own exporters. Downstream users may well select `legacy` by name, and the repo can't show that either way.
- The package is at version 2.3.0. Removing a selectable exporter would be a breaking change in a minor or patch release under semver.

So "unused" is not established. It means only that nothing in this repo imports the function directly.

### What happens if only the function is deleted
- The `legacy` entry in `pyproject.toml` would point at a missing attribute.
- After reinstall, `exporter("legacy")` would raise `AttributeError` when it loads the entry point. Before reinstall, a stale installed entry point would fail the same way.
- Nothing in the repo would catch this, because no test exercises `legacy`.

### What the request leaves undecided
1. **Is the `legacy` exporter meant to be removed as a user-facing feature?** If it is, the `pyproject.toml` entry has to be removed too. If external users may depend on it, the request needs a deprecation path instead of plain deletion.
2. **If it is removed, what is the versioning and communication plan?** That covers a major version bump or a deprecation warning first, and any changelog note. No changelog exists in the repo.
3. **Scope.** Does "delete the function" include the entry-point line, or is the entry point deliberately staying? Leaving it would break `exporter("legacy")`, so I would not recommend that.

### What has to be settled first
The requester has to decide whether the `legacy` exporter name is part of the supported public interface. That is a product and compatibility decision. The repo can't answer it, and it determines whether to delete outright, deprecate first, or keep the function.

If the answer is "remove it outright", the change is small. It means deleting the function, deleting `pyproject.toml:9`, and optionally adding a test that `exporter("legacy")` is no longer registered.

OPEN-DECISIONS: 1
