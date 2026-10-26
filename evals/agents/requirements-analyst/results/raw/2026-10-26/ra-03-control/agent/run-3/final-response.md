# Requirements analysis: `--version` flag for greeter

## Established facts

- `src/greeter/__init__.py` defines `__version__ = "1.4.2"` (line 3).
- `src/greeter/cli.py` has `build_parser()`, which creates `ArgumentParser(prog="greeter")` with one option, `--name` (default `world`). It also has `main(argv=None) -> int`, which parses the arguments, prints `Hello, {name}!` and returns 0.
- `cli.py` does not import anything from the `greeter` package today.
- `tests/test_cli.py` has two tests, `test_default_greeting` and `test_named_greeting`. Both call `main([...])`, assert that it returns 0, and compare `capsys.readouterr().out` to an exact string.
- I did not read the packaging configuration (for example `pyproject.toml`) or look for a console-script entry point. The request doesn't depend on either.

## Inferences

- argparse's `action="version"` writes the version string plus a newline to stdout (Python 3.4 and later) and raises `SystemExit(0)`. With `version=__version__` the output is `1.4.2\n`, which matches "exactly the value ... followed by a newline".
- Do not use a format such as `"%(prog)s 1.4.2"`. It would add a prefix that the request excludes.
- Exit behavior differs from the existing tests. `main(["--version"])` would not return 0 under the argparse action. It would raise `SystemExit` with code 0, and the existing `assert main(...) == 0` pattern would not work for it.
- The new test therefore needs `pytest.raises(SystemExit)`, followed by a check that `excinfo.value.code == 0`. It also needs a check that `capsys.readouterr().out == f"{__version__}\n"`.
- Compare against the imported `__version__` rather than the literal `"1.4.2"`. That keeps the test valid after a version bump and tests the "exactly `__version__`" requirement.

## Proposed acceptance criteria

1. `main(["--version"])` writes `__version__ + "\n"` to stdout and nothing else, writes nothing to stderr, and exits with status 0.
2. The `--version` value is read from `greeter.__version__` and not duplicated as a literal.
3. `main([])` and `main(["--name", "Ada"])` behave as before. The two existing tests pass unchanged.
4. A new test in `tests/test_cli.py` covers `--version`. It follows the file's naming style (`test_version_flag`) and its `capsys` usage, and it asserts the exit status, stdout and empty stderr.
5. The full test suite passes. Run it before reporting completion.

## Unresolved points (implementer-level)

- **Mechanism.** The choices are argparse's built-in version action, or a manual check that prints and returns 0 from `main`. The request's wording ("exits with status 0") fits the built-in action. A manual check would change what the test asserts: `main()` would return 0 instead of raising `SystemExit`. Either meets the stated behavior, and the requester has not said which they want. I treat it as an implementation choice rather than a requester decision.
- **Combined flags.** `--version --name X` is not specified. With the built-in action, `--version` exits during parsing and no greeting is printed. This is the conventional behavior and I assume it is acceptable.

## Risks

- A test written like the existing ones (`assert main(["--version"]) == 0`) would error with an uncaught `SystemExit`.
- A `%` character in a future `__version__` would be treated as a format specifier by argparse. This is not a concern for `1.4.2`.

## Recommended next action

Implement with `parser.add_argument("--version", action="version", version=__version__)` and import `__version__` from `greeter`. Add the `SystemExit`-based test. Run the test suite in the foreground and report the result. No requester input is needed first.

OPEN-DECISIONS: 0
