# Requirements analysis: delete `legacy_export`

## Established facts

- `legacy_export` is defined at `src/reportkit/export.py:19-21`. It renders rows in the tab-separated layout of reportkit 1.x.
- A repository-wide grep finds no Python caller. The only other reference is `pyproject.toml:9`: `legacy = "reportkit.export:legacy_export"`. It sits in the `reportkit.exporters` entry-point group.
- `exporter(name)` in `export.py:24-27` resolves exporters through that entry-point group by name. A caller can therefore reach `legacy_export` with `exporter("legacy")`, and no static call site would show it.
- The README says the entry-point group is the public extension mechanism and that downstream packages register their own exporters. The group is therefore a public interface. The `legacy` name is part of it.
- The package is at version 2.3.0. The docstring ties the function to the 1.x layout, so the entry point may be kept for users migrating from 1.x. This is an inference, and nothing in the repository confirms it.
- `tests/test_export.py` covers only `csv_export`. No test touches `legacy_export` or the `legacy` entry point.
- I found no changelog, deprecation notice, or other documentation about `legacy`. I did not examine git history.

## Assessment of "unused"

"Unused" is true only for direct Python references inside this repository. It is not established for the entry point `legacy`. Callers outside the repository, such as downstream code or configuration that calls `exporter("legacy")`, cannot be seen from here.

If only the function is deleted, the entry point in `pyproject.toml` still points at `reportkit.export:legacy_export`. This leaves a dangling entry point. Any `exporter("legacy")` call would fail with an `AttributeError` (or `ImportError`) from `entry.load()`, instead of a clear "not found" error. Note that installed metadata is generated from `pyproject.toml` at install time, so existing installs would keep the stale entry until they are reinstalled.

## Assumptions

- Unconfirmed: the requester knows `legacy` is registered as an entry point and still wants the function removed.
- Unconfirmed: nobody outside this repository uses `exporter("legacy")`.
- Unresolved: whether removing a public exporter name in a 2.x release is acceptable, or needs a deprecation period or a major-version bump.

## Proposed acceptance criteria

1. `legacy_export` no longer exists in `src/reportkit/export.py`.
2. `pyproject.toml` has no entry point that references `legacy_export`, if the requester confirms the removal. Otherwise the request is changed.
3. A grep for `legacy_export` and for `legacy` as an exporter name returns nothing in source, config, or docs, apart from any intentional changelog note.
4. `csv_export` and `exporter("csv")` behave as before, and the existing test passes.
5. The expected result of `exporter("legacy")` after the change is stated. Either it raises the standard not-found error from the unpacking in `exporter`, or it has a defined replacement behavior.
6. The edit stays limited to the function and its registration, with no unrelated cleanup. The `exporter` function and the `entry_points` import stay, because `csv` still uses them.

## Risks

- A breaking change to a public extension point could affect downstream users, and the repository cannot show who they are.
- A partial deletion (function only) leaves a broken entry point.
- Nothing tests the `legacy` path, so a regression there would not be caught.

## Decisions for the requester

1. **Entry point:** may the `legacy` entry point in `pyproject.toml` be removed together with the function? Removing the function alone leaves a dangling entry point.
2. **Compatibility policy:** is dropping the public `legacy` exporter acceptable in 2.3.0 without a deprecation step or a version bump? Does the requester know of external users?

## Recommended next action

Ask the requester to settle the two decisions above before implementation. If they confirm removal of the function and the entry point, the change is small: delete the function, delete line 9 of `pyproject.toml`, and optionally add a test that `exporter("legacy")` fails as expected. No code has been changed.

OPEN-DECISIONS: 2
