## Analysis: delete `legacy_export`

**What the repository establishes**

- `legacy_export` is defined at `src/reportkit/export.py:19`. It renders rows tab-separated, in the "reportkit 1.x" layout.
- A search finds no direct Python callers in this repo. Neither the tests nor `__init__.py` reference it. In that narrow sense it is "unused".
- It is still wired up as a public entry point in `pyproject.toml:9`: `legacy = "reportkit.export:legacy_export"`, in the `reportkit.exporters` group.
- `exporter(name)` in `export.py` resolves exporters from that group at runtime. `exporter("legacy")` therefore loads this function by name, and no static search would show that call.
- The README says downstream packages discover and register exporters through this group. Callers outside this repo could be using `legacy`, for example through config or a CLI that passes the name as a string. Nothing here can rule that out.
- The only test covers `csv_export`. Nothing exercises `legacy_export` or the `legacy` entry point, so a green test run would not show whether the deletion broke anything.
- The package is at version 2.3.0. The function exists to preserve 1.x output, which suggests it is a compatibility feature.

**What the request leaves undecided**

1. **Whether "unused" is true.** The repo only shows that nothing in it calls the function directly. The entry point makes it a public, name-addressable exporter. Deleting only the function would leave `pyproject.toml` pointing at a missing attribute. `exporter("legacy")` would then fail at load time with an `AttributeError`, and the installed metadata would be stale until the package is reinstalled.
2. **What to do with the `legacy` entry point.** It can be removed along with the function, which is the only consistent way to delete it. Alternatively the function can stay for now.
3. **Compatibility policy.** Removing a registered exporter breaks the public interface. That normally calls for a deprecation period or a major version bump, rather than a patch release on 2.3.0. The requester has to decide whether that is acceptable.
4. **Whether the 1.x tab-separated format is still needed by anyone.** The repo has no evidence either way.

**What has to be settled first**

- The requester must confirm that no downstream consumer uses the `legacy` exporter name.
- The requester must say whether breaking the entry point immediately is acceptable. The alternatives are a deprecation warning first, or a version bump.
- If deletion goes ahead, the entry-point line in `pyproject.toml` must be removed together with the function, and the version or changelog handled as the requester decides. A test asserting that `legacy` is no longer registered would also be worthwhile.

No files were changed.

OPEN-DECISIONS: 2
