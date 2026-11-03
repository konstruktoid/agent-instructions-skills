The fix does not hold up. `ruff check` fails, and the loader it chose is still unsafe for untrusted YAML.

- **`ruff check .`: unresolved.** `src/cfgload/config.py:11:41` fails with `S506 Probable use of unsafe loader FullLoader with yaml.load. Allows instantiation of arbitrary objects. Consider yaml.safe_load.` The error count is 1.
- **`ruff format --check .`: confirmed clear.** It reports 19 files already formatted.
- **`ty check`: confirmed clear.** It reports all checks passed.
- **Suppressions: confirmed clear.** `pyproject.toml` selects `S`, and no `S` rule is disabled or suppressed.
- **No untrusted data reaches `yaml.load`: unresolved.** `src/cfgload/config.py:11` still calls `yaml.load(handle, Loader=yaml.FullLoader)` on tenant-uploaded YAML.
  - `references/deserialization.md` allows only `yaml.safe_load` or `Loader=yaml.SafeLoader` on untrusted YAML. It says never to use `yaml.load` with an unsafe loader.
  - `FullLoader` is only a partial hardening of `Loader`. It still builds Python objects from tags. The tooling flags it, and PyYAML's own docs say not to use it on untrusted input.
  - The fix swapped one unsafe loader for another instead of fixing the deserialization class the request named. The pinned PyYAML is 6.0.3.
- **Boundary validation: unresolved.** `load_config` is annotated `-> dict[str, object]`, but nothing checks that the parsed result is a mapping. A tenant file containing a list, a scalar, or an empty document would return something that isn't a dict. I did not test this.
- **Reference files: confirmed clear.** The triage table matches `yaml.load` and uploaded data. I read `deserialization.md`. `injection.md` also matches uploaded data, and I did not read it.
- **Secrets, SSRF, access control, dependency changes, and user or system information in the commit: not applicable.** The diff has one line and touches none of them.

**Next action:** a fresh reviewer pass on the unresolved items. Change line 11 to `yaml.safe_load(handle)`, or to `yaml.load(handle, Loader=yaml.SafeLoader)`. Add a check that the result is a `dict` and fail closed otherwise. Then rerun `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.

VERDICT: UNRESOLVED
