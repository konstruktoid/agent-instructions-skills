# Requirements analysis: delete `legacy_export`

## Established facts

- `src/reportkit/export.py:19-21` defines `legacy_export(rows)`. It renders rows in the tab-separated layout of reportkit 1.x. (Source: file read.)
- A repository-wide search finds no Python call site or import of `legacy_export`. The tests cover only `csv_export` (`tests/test_export.py`). In the narrow sense, no code in this repository calls the function.
- `pyproject.toml:9` registers it as an entry point: `legacy = "reportkit.export:legacy_export"` in the `reportkit.exporters` group.
- `exporter(name)` in `export.py:24-27` resolves exporters by name through that group and calls `entry.load()`. The function is therefore reachable at runtime through `exporter("legacy")`, and the name does not appear as a string literal in the code.
- `README.md` states that exporters are discovered through this entry-point group and that downstream packages can register their own. The group is a documented extension surface, and `legacy` is one of its two built-in names.
- The package is at version 2.3.0. The docstring ties `legacy` to the 1.x layout, which suggests it exists for compatibility with older users.

## What "unused" means

The request's premise is that the function is unused. The repository confirms this only for direct references. It contradicts the premise for runtime use, because the entry point makes `legacy_export` loadable by name. The repository cannot show whether anything outside it calls `exporter("legacy")`. Candidates are downstream packages, scripts, and configuration that selects an exporter by name.

## Consequences of a literal deletion

- The entry point in `pyproject.toml` would point to a missing attribute.
- After the package is installed, `exporter("legacy")` would find the entry and fail on `entry.load()` with an `AttributeError`. That failure is worse than a clean "not found" error.
- Removing a name from a documented plugin group is a public-interface change in a 2.x release.

## Assumptions

| Assumption | Status |
|---|---|
| No in-repo Python code calls `legacy_export` | Confirmed |
| The `legacy` entry point should be removed together with the function | Reasonable but unconfirmed |
| No external consumer uses the `legacy` exporter name | Unresolved |
| Removing it is acceptable in a minor or patch release under the project's versioning policy | Unresolved (no policy found in the repository) |
| Installed metadata (egg-info or dist-info) may be stale until reinstall | Reasonable but unconfirmed |

## Proposed acceptance criteria

1. `legacy_export` no longer exists in `src/reportkit/export.py`.
2. `pyproject.toml` has no entry point that references `legacy_export`. Alternatively, the requester explicitly decides to keep the entry point and keep the function.
3. No reference to `legacy_export` remains anywhere in the repository (`grep` returns nothing).
4. `csv_export` and `exporter("csv")` behave as before, and the existing test passes.
5. After reinstalling the package, `exporter("legacy")` either fails with the chosen, documented error or is deprecated per the requester's decision.
6. Version and changelog handling follows the requester's choice. No changelog file exists in the repository.

## Unresolved decisions (requester only)

1. **Entry point and compatibility.** The options are as follows.
   - (a) Remove the function and the `legacy` entry point as a breaking change.
   - (b) Deprecate first, with a warning and removal in a later major release.
   - (c) Keep the function because the entry point makes it used.
2. **External consumers.** Confirm whether any downstream package or user relies on the `legacy` exporter name. The repository cannot answer this.
3. **Versioning.** If the function is removed, decide whether the release is a major bump or whether 2.3.0 policy allows removal in a minor release.

## Risks

- Deleting only the function, as literally requested, leaves a broken entry point that fails at load time.
- External breakage cannot be detected from this repository.
- The existing test suite would not catch either problem, because nothing tests `exporter("legacy")`.

## Recommended next action

Do not implement yet. Ask the requester to settle decision 1, and decision 2 if they can, since decision 3 follows from them. If the answer is (a), the change is limited to deleting the function and the `pyproject.toml` line. A test asserting that `legacy` is not registered would then be reasonable but is not requested.

OPEN-DECISIONS: 3
