# Analysis: delete `legacy_export`

## Established facts
- `legacy_export` is defined at `src/reportkit/export.py:19-21`. It renders rows as tab-separated text, the "layout of reportkit 1.x".
- A search of the repository, excluding `.git`, finds no direct Python caller of `legacy_export`. The only other reference is `pyproject.toml:9`, which registers it as an entry point:
  `[project.entry-points."reportkit.exporters"] legacy = "reportkit.export:legacy_export"`.
- `exporter(name)` at `export.py:24-27` looks up entry points in the group `reportkit.exporters` and loads the one with that name. A caller can therefore reach `legacy_export` with `exporter("legacy")`, and no name appears in the code. Searching for the function name therefore doesn't show whether it is used.
- The project is `reportkit` version 2.3.0. Whether anything outside this repository uses the `legacy` exporter is unknown. I found no tests, README mention, or changelog that says so.

## Contradiction
The request calls the function "unused", but that holds only for direct references. It is a registered, publicly selectable exporter. The claim of "unused" is not established by the repository.

## Consequences if only the function is deleted
- The entry point `legacy` in `pyproject.toml` would still point at a missing attribute.
- `exporter("legacy")` would raise `AttributeError` when it loads the entry point.
- Installed metadata would stay stale until reinstall.

## Assumptions
- Unresolved: that no external consumer calls `exporter("legacy")` or selects `legacy` by name, for example a CLI, config file, or downstream package.
- Reasonable but unconfirmed: the requester wants the `legacy` entry point removed too. Otherwise the package is left broken.
- Unresolved: whether removing a user-selectable exporter is acceptable in a 2.3.0 release. Under semantic versioning this is a breaking change, and it might call for deprecation first.

## Proposed acceptance criteria (once decisions are settled)
1. `legacy_export` no longer exists in `export.py`.
2. The `legacy = ...` line is removed from `pyproject.toml`, if the requester chooses full removal.
3. A repository search for `legacy_export` and for the `legacy` exporter name returns nothing, except in any changelog entry.
4. `csv_export` and `exporter("csv")` behave as before.
5. `exporter("legacy")` fails in the way the requester chose. The default is "no such entry point", which is a `ValueError` from the tuple unpack because no entry matches.
6. Tests and import checks pass. I found no test suite in the repository, so a check for that is needed.

## Decisions only the requester can make
1. **Entry point:** Remove the `legacy` entry point as well, or keep it? Keeping it would require keeping the function, which contradicts the request.
2. **Compatibility:** Is dropping `legacy` acceptable now, or should it go through a deprecation period first, with a warning and a later removal? Do any known external users depend on it, and does the version number or a changelog need to change?

## Risks
- Deleting only the function breaks `exporter("legacy")` at runtime.
- External users of the 1.x tab-separated format may break silently.
- There is no test coverage to catch either problem.

## Recommended next action
Ask the requester the two questions above. Don't edit anything until they answer.

OPEN-DECISIONS: 2
