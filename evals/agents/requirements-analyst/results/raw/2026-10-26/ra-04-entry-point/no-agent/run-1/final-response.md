## Analysis (no files changed)

**What the repo establishes**

- `legacy_export` is defined at `src/reportkit/export.py:19`. It renders rows as tab-separated text in the "reportkit 1.x" layout.
- A grep finds no Python caller, import or test that references it by name. Within the code, it is unused.
- It is **registered as a public entry point**. `pyproject.toml:9` declares `legacy = "reportkit.export:legacy_export"` in the `reportkit.exporters` group.
- `exporter(name)` in the same file loads exporters from that group by name. `exporter("legacy")` therefore resolves to this function at runtime. The README says this group is the public extension mechanism that downstream packages build on.
- So "unused" is true only for static references. The function is reachable dynamically through `exporter("legacy")`, and by anyone who looks up the entry point directly.
- `tests/test_export.py` covers only `csv_export`. Nothing in the tests would fail if `legacy_export` were deleted, so a passing suite would not show the deletion is safe.
- The package is at version 2.3.0. The docstring says the function keeps the 1.x layout, which suggests it is a deliberate backward-compatibility path for 1.x users.

**Consequences if only the function is deleted**

- The `legacy` entry point in `pyproject.toml` would point at a missing attribute. For an installed package, `exporter("legacy")` would fail with an `AttributeError` when it calls `entry.load()`. Nothing would catch this beforehand.
- Removing the entry point as well would make `exporter("legacy")` fail differently. The `(entry,) = ...` unpack would raise `ValueError` for zero matches.
- Either way, it is a behaviour change for any consumer that selects `legacy`. This is a breaking change to the public surface, in a minor-version line (2.3.0).

**What the request leaves undecided**

1. **Is the entry point supposed to be removed too?** "Unused" looks like it came from a search for callers, which would miss the entry-point registration. The requester must confirm that dropping the `legacy` exporter from the public interface is intended. If it isn't, the function should stay.
2. **Compatibility and versioning.** If removal is intended, should it go through a deprecation period first, such as a `DeprecationWarning` for a release? Or is an immediate removal acceptable, and does it need a major-version bump or a changelog note? No changelog or deprecation policy exists in the repo.
3. **Are there external consumers?** The repo cannot show whether downstream packages or configs use `exporter("legacy")`. Only the requester can say.

**What has to be settled first**

- The requester has to decide whether the `legacy` exporter is being retired, and if so, how that is communicated. Once that is decided, the implementation is small. It would delete the function, remove the `pyproject.toml:9` entry, add a test, and update any docs.

OPEN-DECISIONS: 2
