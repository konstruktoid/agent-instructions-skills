## Requirements analysis: `--version` flag for greeter

### Established facts (sources read)
- `src/greeter/cli.py`: `build_parser()` creates `argparse.ArgumentParser(prog="greeter")` with only `--name`. `main(argv)` parses the arguments, prints `Hello, {name}!`, and returns 0. It does not call `sys.exit`.
- `src/greeter/__init__.py`: `__version__ = "1.4.2"`.
- `pyproject.toml`: the package version is also hardcoded as `1.4.2`. The console script `greeter = greeter.cli:main` and `requires-python >=3.11` are also set there. The README has no mention of version.
- `tests/test_cli.py`: two tests call `main([...])`, assert the return value is 0, and check `capsys.readouterr().out`.

### Analysis
- **Output format.** argparse's built-in `action="version"` writes the version to stdout on Python 3.4 and later, followed by a newline. With `version=__version__` the output is exactly `1.4.2\n`, which matches the request. The request asks for the bare value with no program-name prefix, so the format is settled.
- **Exit mechanism.** The built-in action calls `parser.exit()`, which raises `SystemExit(0)`. It does not return 0 from `main`. The existing tests assert `main(...) == 0`, so a new test for `--version` must use `pytest.raises(SystemExit)` and check `.value.code == 0`. The request says "exits with status 0", which this satisfies. It is a different pattern from the existing tests. Returning 0 from `main` instead would need a custom action or a pre-parse check. The request's wording ("exits") supports `SystemExit`.
- **Version source.** The request says to print `__version__` from `__init__.py`. The duplicate in `pyproject.toml` is out of scope, but the two values can drift. This is a risk, not a blocker.
- **Import.** `cli.py` needs `from greeter import __version__`. I found no circular import, because `__init__.py` imports nothing.

### Proposed acceptance criteria
1. `main(["--version"])` raises `SystemExit` with code 0.
2. In that case, stdout is exactly `f"{__version__}\n"` and stderr is empty.
3. The greeting is not printed.
4. A test in `tests/test_cli.py` covers 1–3. It compares against the imported `__version__` and does not hardcode `"1.4.2"`.
5. Existing tests still pass, and `--name` behavior is unchanged.
6. Verification: run `pytest tests/test_cli.py`. I did not run it, because I changed nothing.

### Assumptions
- Confirmed: argparse's version action prints to stdout with a trailing newline on Python ≥3.11.
- Reasonable but unconfirmed: the "-V" short alias is not wanted. The request names only `--version`.
- Reasonable but unconfirmed: raising `SystemExit` is acceptable for "exits with status 0", even though `main` otherwise returns an int.

### Unresolved decisions
None require the requester before implementation can start. The request fixes the flag name, output, exit status, and test location. The `SystemExit` versus return-0 question is settled by the request's own wording, and I flag it only so the implementer knows the test shape differs from the existing ones.

### Risks
- The `pyproject.toml` version can drift from `__version__`. This is out of scope and I recommend leaving it.
- A test that hardcodes `"1.4.2"` would break on a version bump.

### Recommended next action
Proceed with the implementation: add `action="version", version=__version__` to the parser, import `__version__`, and add the `SystemExit`-based test. Keep the change minimal.

OPEN-DECISIONS: 0
