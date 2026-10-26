**Analysis: `--version` flag for `greeter`. No code was changed.**

**What the repository establishes**
- `src/greeter/cli.py` has `build_parser()`, which creates an `ArgumentParser(prog="greeter")` with one option, `--name` (default `"world"`).
- `main(argv=None) -> int` parses the arguments, prints `Hello, {name}!` and returns 0. The console script is `greeter = "greeter.cli:main"`.
- `src/greeter/__init__.py` defines `__version__ = "1.4.2"`.
- `pyproject.toml` also hardcodes `version = "1.4.2"`. It is static, so it is a second copy of the version, and the two currently agree.
- `cli.py` doesn't import from the `greeter` package yet. A `from greeter import __version__` would work, since the tests already import `greeter.cli`.
- `tests/test_cli.py` has two tests, `test_default_greeting` and `test_named_greeting`. Each calls `main([...])`, asserts the return value is 0 and checks `capsys.readouterr().out`.
- There is no existing `--version` handling.

**Behavior to account for when implementing**
- The obvious route is argparse's `action="version"` with `version=__version__`. It writes the version plus a newline to stdout and then raises `SystemExit(0)`.
- Because of that, `main(["--version"])` will not return 0 like the other paths do. The new test must use `pytest.raises(SystemExit)` and check `excinfo.value.code == 0`, plus `out == "1.4.2\n"`. Running the installed `greeter --version` still exits with status 0, so the request is met either way.
- The alternative is a manual flag that prints and returns 0. That keeps the `main()` return-value convention but bypasses argparse's built-in handling. Either meets the stated requirements, so this is an implementation choice and not a requester decision.
- The output must be exactly the version string. A custom label such as `greeter 1.4.2` would violate the request, and argparse applies `%`-formatting to the version string. That is harmless for `"1.4.2"`.
- The test should compare against the imported `__version__`, not a hardcoded `"1.4.2"`, so it doesn't break on version bumps.

**What the request leaves undecided**
- The request is specific about the flag name, the output, the exit status, the source of the value and the test location, so nothing blocks implementation.
- The short flag `-V` and the `pyproject.toml` version duplication are out of scope. The request names only `--version`, so I would not add either.

**What has to be settled first**
- Nothing.

OPEN-DECISIONS: 0
