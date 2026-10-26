# Requirements analysis: delete `legacy_export`

## Established facts
- `legacy_export` is defined at `src/reportkit/export.py:19-21`. It renders rows in the tab-separated layout of reportkit 1.x.
- No Python code, test or README references it. A grep for `legacy_export` finds only its definition and `pyproject.toml:9`.
- `pyproject.toml:9` registers it as a public entry point: `legacy = "reportkit.export:legacy_export"`, in the `reportkit.exporters` group.
- `exporter(name)` at `export.py:24-27` loads exporters by name from that group. Callers, including external ones, can therefore reach `legacy_export` through `exporter("legacy")` without ever naming the function.
- The package is at version 2.3.0 and has no dependencies. `tests/test_export.py` exists, but the grep found nothing in it about `legacy`.

## Why "unused" is not established
- The repository shows no direct callers. It does not show that nobody calls the exporter by name.
- Entry-point lookup is dynamic, so a static grep cannot prove the function is unused. Downstream packages or scripts may call `exporter("legacy")`. The docstring suggests it exists for 1.x-compatible output, which is the kind of thing external users depend on.
- If only the function is deleted, the `legacy` entry point stays registered. After reinstalling, `exporter("legacy")` would then fail at `entry.load()` with an `AttributeError`. A stale installed distribution would still point at a function that no longer exists.
- Every other `exporter(name)` call would be unaffected. The `(entry,) = ...` unpacking only matters for the `legacy` name.

## Assumptions
- Confirmed: there are no in-repo callers.
- Reasonable but unconfirmed: the requester means "unused" in the in-repo sense.
- Unresolved: whether external consumers use the `legacy` exporter. The repository cannot answer this.
- Unresolved: whether removing a public exporter in a 2.x release is acceptable. Removal may call for a deprecation period or a major version bump.

## Proposed acceptance criteria
1. `legacy_export` no longer exists in `export.py`.
2. `pyproject.toml` has no `legacy` entry point, so no entry point refers to a missing target. This depends on decision 1.
3. `csv_export` and `exporter("csv")` behave as before, and the test suite passes.
4. A grep for `legacy_export` and for the `legacy` exporter name finds no remaining references. This includes docs and changelog, apart from any deliberate removal note.
5. The version or changelog handling matches the answer to decision 2.

## Open decisions (requester only)
1. **Entry point:** Should the `pyproject.toml` `legacy` entry point be removed along with the function? Removing both is the only consistent option, because deleting only the function breaks `exporter("legacy")`. But it removes a public interface, so the requester must confirm it.
2. **Compatibility:** Is removing a public, 1.x-compatibility exporter acceptable without a deprecation period or version bump? Does the requester know that no external users depend on it?

## Risks
- A silent break for downstream users of `exporter("legacy")`.
- A broken installed distribution if the function is deleted but the entry point stays.
- A deletion that is hard to reverse once a release ships.

## Recommended next action
Ask the requester to confirm decisions 1 and 2. If the answer is "remove both, no deprecation", the change is small: delete the function and the `pyproject.toml` line, then run the tests. Do not delete only the function.

OPEN-DECISIONS: 2
