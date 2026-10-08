The fix doesn't hold up. `ruff check` fails, and the loader it switched to is still unsafe for untrusted YAML.

- **`ruff check .`: unresolved.** It reports `S506` at `src/cfgload/config.py:11:41`: "Probable use of unsafe loader `FullLoader` with `yaml.load`. Allows instantiation of arbitrary objects. Consider `yaml.safe_load`."
- **`ruff format --check .`: confirmed clear.** It reported 18 files already formatted.
- **`ty check`: confirmed clear.** It reported "All checks passed!"
- **Suppressions: confirmed clear.** `select` includes `S`, and the commit adds no ignore or `noqa`. That is the only thing that holds, because the change swaps the loader and nothing else.
- **Class of issue (unsafe deserialization of tenant-uploaded YAML): unresolved.** `deserialization.md` says to use `yaml.safe_load` or `Loader=yaml.SafeLoader`, and never `yaml.load` on untrusted YAML (`S506`). `FullLoader` is still `yaml.load` with a loader that can instantiate Python objects from tags. The uploads are untrusted, so the trust-boundary check also fails. The change only moves the problem from `yaml.Loader` to `yaml.FullLoader`.
- **Untrusted data reaching `yaml.load` (checklist item): unresolved.** Tenant YAML still goes to `yaml.load` at `config.py:11`.
- **Boundary validation of the parsed mapping: unresolved.** The function is annotated as returning `dict[str, object]` but returns whatever the parser produces, with no check that the top level is a mapping. This is lower severity than the loader.
- **Reference files read: confirmed clear.** I read `deserialization.md` and `injection.md`, which are the files the triage table matches for `yaml.load` and uploaded data.
- **Other checklist items: not applicable.** The change touches no secrets, crypto, SSRF, access control, dependencies, or committed user information.

Next action: a fresh reviewer pass that replaces the call with `yaml.safe_load(handle)`, or `yaml.load(handle, Loader=yaml.SafeLoader)`. The pass should also validate that the result is a mapping and then rerun `ruff` and `ty`.

VERDICT: UNRESOLVED
