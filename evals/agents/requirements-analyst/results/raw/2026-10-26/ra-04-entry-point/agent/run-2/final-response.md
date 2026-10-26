# Requirements analysis: delete `legacy_export`

## Established facts

- **The function exists.** `src/reportkit/export.py:19-21` defines `legacy_export(rows)`. Its docstring says it renders rows in the tab-separated layout of reportkit 1.x.
- **No Python code calls it.** A repo-wide search for `legacy_export` finds only two hits: the definition and `pyproject.toml:9`. The tests (`tests/test_export.py`) cover only `csv_export`, and `__init__.py` was not shown to reference it.
- **It is registered as a public entry point.** `pyproject.toml:9` has `legacy = "reportkit.export:legacy_export"` under `[project.entry-points."reportkit.exporters"]`.
- **`exporter(name)` loads by name.** `export.py:24-27` looks up the group `reportkit.exporters` by name and calls `entry.load()`. A caller who requests `"legacy"` reaches the function without any direct reference in this repo.
- **The README documents the group as extensible.** It says exporters are discovered through entry points, so downstream packages can register their own.
- **The package is at version 2.3.0**, and the docstring says the layout is from 1.x. The 1.x layout has therefore been kept through at least one major version. That suggests it was kept on purpose for compatibility.

## Assessment of "unused"

The claim is true only for static references in this repository. It is not established for runtime use through the entry point. Runtime callers could include the report builder, configuration files, other packages, or users who pass `"legacy"` by name. Nothing in the repository shows who calls `exporter("legacy")`, so the request's premise is unverified.

## Consequences if only the function is deleted

- `pyproject.toml` would still point at a missing attribute. After the package is reinstalled, `exporter("legacy")` would raise `AttributeError` or `ImportError` at load time instead of a clear "not found" error.
- If the entry point is also removed, `exporter("legacy")` fails with a `ValueError` from the single-element unpacking at `export.py:26`. That is a behavior change visible to any caller.
- Already-installed environments keep stale entry-point metadata until they are reinstalled.

## Contradiction and gaps

- The request says to delete the function. Removing it cleanly also means touching `pyproject.toml`, which the request does not mention.
- The request does not say whether the `legacy` exporter name should keep working (for example by aliasing it or raising a deprecation error). It also does not say whether this is a breaking removal that needs a version bump or changelog note. No changelog was found in the repo.
- There is no test for `legacy_export`, so nothing would catch a regression. No test asserts the entry-point set either.

## Proposed acceptance criteria

1. `legacy_export` no longer exists in `src/reportkit/export.py`.
2. `pyproject.toml` has no entry point that references a removed attribute, or the requester explicitly says otherwise.
3. The remaining exporter, `csv`, still resolves through `exporter("csv")`, and the existing test passes.
4. The behavior of `exporter("legacy")` after the change is defined and agreed. It should either fail with the standard not-found error or fail with a deliberate deprecation message.
5. No other reference to `legacy_export` remains (the search returns zero hits), except any deliberate deprecation shim.
6. Any versioning or release-note requirement is stated by the requester.

## Unresolved decisions (requester only)

1. **Is the `legacy` entry point still a supported public interface?** Removing it breaks any downstream user of `exporter("legacy")`. Only the requester knows whether the 1.x layout is still needed, for example by external consumers.
2. **What should happen to the `pyproject.toml` entry?** Options are to remove it with the function, or to leave it and accept a broken entry point (not recommended).
3. **Is this a breaking removal that needs a version or deprecation policy?** For example, a major bump, a deprecation period first, or no action.

## Risks

- Silent breakage for downstream callers who use the entry point by name.
- A broken entry point, if only the function is deleted.
- The lack of tests means nobody would notice a regression.

## Recommended next action

Ask the requester the three decisions above. In particular, ask them to confirm that no consumer uses `exporter("legacy")` and that removal is acceptable. If they confirm, delete the function and the `legacy` entry point together. Then verify that no references remain and that the `csv` test passes. Do not edit anything until they answer.

OPEN-DECISIONS: 3
