# Analysis: delete `legacy_export` from src/reportkit/export.py

## Established facts
- `legacy_export` is defined at `src/reportkit/export.py:19-21`. It renders rows in the tab-separated layout of reportkit 1.x.
- A grep for `legacy_export` finds two places that mention it: its definition and `pyproject.toml:9`.
- `pyproject.toml:9` registers it as the `legacy` exporter: `legacy = "reportkit.export:legacy_export"` in the `reportkit.exporters` entry-point group.
- `exporter(name)` in `export.py:24-27` loads exporters by name from that group. Any caller can therefore reach the function as `exporter("legacy")` with no textual reference to `legacy_export`.
- README.md says the entry-point group is the public discovery mechanism, and that downstream packages register their own exporters. The package is at version 2.3.0.
- `tests/test_export.py` covers only `csv_export`. No test references `legacy_export` or the `legacy` entry point.

## Assessment of the "unused" premise
- The premise is **not confirmed**. Within this repository, no Python code calls the function directly. It is still registered as a public entry point, so it is used through lookup by name.
- The repository can't show whether outside callers use `exporter("legacy")`. That includes users still on the 1.x layout, and it could include downstream packages or configuration outside this repo. Grep can't settle this, and nothing in the repo records usage.
- If the function is deleted and `pyproject.toml` is left alone, the `legacy` entry point would point at a missing attribute. `exporter("legacy")` would then raise `AttributeError` when it loads the entry point. The installed metadata may also be stale until the package is reinstalled.

## Proposed acceptance criteria
1. `legacy_export` no longer exists in `export.py`.
2. The `legacy` entry in `pyproject.toml` is handled consistently with that. It is either removed together with the function, or the function is kept. No dangling entry point remains.
3. `csv_export` and the `csv` entry point are unchanged. `tests/test_export.py` passes.
4. If the removal is deliberate, `exporter("legacy")` has a defined outcome. At present it would fail with `ValueError` from the tuple unpack, because no entry matches. After the removal it should be a documented failure, not an incidental one.
5. Any needed version or changelog note is recorded, according to the decision below. No changelog file exists in the repo.

## Unresolved decisions (requester only)
1. **Is the `legacy` exporter intentionally being retired as a public interface?** Removing a registered entry point is a breaking change for anyone who calls `exporter("legacy")`. The request calls the function "unused", but the entry point contradicts that. The requester needs to either confirm the removal is intended or withdraw it.
2. **If it is retired, what is the compatibility policy?** The options are an immediate removal, a deprecation period (for example, a warning first), or a version bump. The package is at 2.3.0, and semver would normally call for a major bump or a deprecation cycle. That is the requester's call.

## Risks
- Deleting only the function breaks `exporter("legacy")` at runtime. No existing test would catch it.
- Downstream packages and 1.x-format consumers may depend on it. This can't be verified from the repository.
- The repository has no test for the `legacy` path, so a regression check would have to be added or done by hand.

## Recommended next action
Ask the requester to confirm that the `legacy` public exporter is being retired, and which compatibility policy applies. Once that is settled, remove both the function and the `pyproject.toml` entry together. Then run the test suite and check that `exporter("legacy")` fails as intended.

OPEN-DECISIONS: 2
