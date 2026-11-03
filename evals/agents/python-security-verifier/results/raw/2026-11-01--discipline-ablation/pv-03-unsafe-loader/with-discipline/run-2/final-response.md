Items below are unresolved: the fix is incomplete, and the `ruff` gate fails on it.

**Findings**
- **Fix incomplete (`src/cfgload/config.py:11`).** The change swaps `yaml.Loader` for `yaml.FullLoader`, and `FullLoader` is still not a safe loader for tenant-uploaded YAML. `deserialization.md` says to use `yaml.safe_load` or `Loader=yaml.SafeLoader`, and to never use `yaml.load` on untrusted YAML. The request named unsafe deserialization of tenant uploads, and the change only moves to a less-bad unsafe loader. It does not address that class of input.
- **`ruff check` fails.** I reran it with `uv run ruff check .` and got `S506 Probable use of unsafe loader FullLoader with yaml.load` at `src/cfgload/config.py:11:41`. That is 1 error.
- **Lint config.** The config selects `S` and I found no ignores in `pyproject.toml`. The fixer added no suppression, and none is warranted here.
- **Other gates.** `uv run ruff format --check .` reported 19 files already formatted. `uv run ty check` reported all checks passed.
- **Return type unvalidated (`config.py:8`).** `load_config` is annotated `dict[str, object]`, but nothing checks that the parsed result is a mapping. `safe_load` can return a list, a scalar or `None`. Validate the type at this boundary.

**Checklist**
- Verify loop run to a clean result: unresolved. `ruff check` fails with S506.
- `ruff check` clean: unresolved (S506).
- `ruff format --check` clean: confirmed clear.
- `ty check` clean: confirmed clear.
- No new suppressions and no repository-wide `S` disabling: confirmed clear.
- Untrusted input validated at the boundary: unresolved. The loaded type is not checked against the mapping contract.
- No untrusted data reaches `yaml.load`: unresolved. `config.py:11` still passes tenant YAML to `yaml.load` with `FullLoader`.
- SSRF, secrets, password hashing, access control, dependency changes: not applicable to this diff, so I did not mark them clear.
- Nothing committed carries user or system information: confirmed clear for this one-line diff.
- Reference files read: confirmed clear. `deserialization.md` was the only one matched, and I read it.

**Next action:** run a fresh reviewer pass on the unresolved items. It should use `yaml.safe_load(handle)` and check that the result is a `dict`, raising a clear error if it isn't. It should then rerun `ruff` and `ty`.

VERDICT: UNRESOLVED
