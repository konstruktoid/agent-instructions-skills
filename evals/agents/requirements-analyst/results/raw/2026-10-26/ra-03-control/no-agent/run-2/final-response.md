**Current behavior (from the repo)**
- `src/greeter/cli.py`: `build_parser()` makes an `argparse.ArgumentParser(prog="greeter")` with one option, `--name` (default `"world"`). `main(argv)` parses the arguments, prints `Hello, {name}!` and returns `0`. It returns the status rather than calling `sys.exit`. `pyproject.toml` wires `greeter = "greeter.cli:main"` as the console script.
- `src/greeter/__init__.py`: `__version__ = "1.4.2"`. `pyproject.toml` also hardcodes `version = "1.4.2"`, so the version is stored in two places that currently agree.
- `tests/test_cli.py`: two tests call `main([...])`, assert the return value is `0`, and check stdout with `capsys`.

**What the request settles**
- The flag is `--version`.
- Its output is the bare `__version__` value plus `\n`, with no `greeter` prefix.
- The exit status is 0.
- The test goes in `tests/test_cli.py`.

**Points the request leaves open, none of which block implementation**
1. **Exit mechanism.**
   - `argparse`'s `action="version"` calls `sys.exit(0)` inside `parse_args`. So `main(["--version"])` raises `SystemExit(0)` and does not return `0` like the existing tests expect.
   - The test therefore needs `pytest.raises(SystemExit)` and a check that `.code == 0`. The alternative is a custom check in `main` that returns `0`.
   - Both meet "exits with status 0". As a CLI it behaves the same either way, and the repo's console-script entry would pass the return value to `sys.exit` anyway. I'd use the standard `action="version"` with `version=__version__`, because the exact-output requirement is met either way.
2. **Output stream.** `action="version"` prints to stdout on Python 3.11 and later, which matches `requires-python`. The test can check `capsys.readouterr().out == "1.4.2\n"`. Better to compare against the imported `__version__` than a literal, so the test doesn't break on a version bump.
3. **Duplicate version in `pyproject.toml`.** The request names only `__init__.py` as the source, so that is the one to use. Syncing the two copies is out of scope and no change is needed.
4. **Short flag `-V`.** It isn't requested, so it won't be added.
5. **Help text.** Wording for the `--version` help line isn't specified. The implementer can pick something conventional.

None of these are decisions that only the requester can make. The request is specific enough to implement as written, and the choices above are conventional defaults.

OPEN-DECISIONS: 0
