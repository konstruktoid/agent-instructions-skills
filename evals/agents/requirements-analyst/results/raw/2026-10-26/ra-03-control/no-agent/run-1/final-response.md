**Analysis (no files changed)**

**What the repository establishes**
- `src/greeter/cli.py` has `build_parser()`, which creates an `argparse.ArgumentParser(prog="greeter")` with one option, `--name` (default `"world"`). `main(argv=None) -> int` parses the arguments, prints `Hello, {name}!`, and returns 0.
- `src/greeter/__init__.py` defines `__version__ = "1.4.2"`. `pyproject.toml` separately hardcodes `version = "1.4.2"`, and the two currently agree.
- The entry point is `greeter = "greeter.cli:main"`.
- `tests/test_cli.py` has two tests, `test_default_greeting` and `test_named_greeting`. Each calls `main([...])`, asserts the return value is 0, and checks `capsys.readouterr().out`.
- I did not check `README.md` for usage text that might need a mention of the flag.

**How the request maps onto this**
- The request names the flag, the output (the exact `__version__` value plus a newline), the exit status (0), and the test location. All of these can be built and checked against the code as it stands.
- `argparse`'s `action="version"` with `version=__version__` fits the output requirement. It writes the version plus a newline to stdout, then raises `SystemExit(0)`.
- Because of that, `main()` never returns in this path. The new test has to use `pytest.raises(SystemExit)`, check `exc.value.code == 0`, and check `capsys.readouterr().out == f"{__version__}\n"`. This differs from the existing tests, which assert on a return value, so the test will look different from its neighbours.
- The test should compare against the imported `__version__`, not a literal. That keeps it correct when the version changes.
- Python 3.9 and later `argparse` writes the version text to stdout, which is what the request needs.
- The `--version` output is not prefixed with `greeter`. This follows the request's "exactly the value".

**Points that are not open decisions**
- The `pyproject.toml` version duplicate is out of scope. The request says to print `__version__`, so `pyproject.toml` stays untouched. Someone may want to deduplicate it later, but that is a separate change.
- A short `-V` alias is not requested, so I would not add one.

**What has to be settled first**
- Nothing blocks implementation. The behavior, the source of the value, the exit status, and the test location are all specified, and the repository is consistent with them.

OPEN-DECISIONS: 0
