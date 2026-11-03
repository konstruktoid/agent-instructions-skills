## Established facts

- `src/greeter/__init__.py` defines `__version__ = "1.4.2"`.
- `src/greeter/cli.py` builds an `argparse.ArgumentParser(prog="greeter")` with one option, `--name`. `main(argv)` calls `parse_args(argv)`, prints `Hello, {name}!`, and returns 0. It has no `--version` option.
- `pyproject.toml` declares `version = "1.4.2"` statically. It matches `__version__` today, but nothing keeps the two in sync. The console script is `greeter = "greeter.cli:main"`.
- `tests/test_cli.py` has two tests. Each calls `main([...])`, asserts a return value of 0, and checks `capsys.readouterr().out`.
- `README.md` documents only `greeter --name Ada`.
- No other source files exist. There is no CI configuration and no `__main__.py`.

## Request analysis

The request says to print exactly the `__version__` value, followed by a newline, and exit with status 0. Both the exact output and the exit status are specified.

**Conflict with argparse's `action="version"` (a fact about the standard library, not read from this repository).** That action prints the version and then calls `parser.exit()`, which raises `SystemExit(0)`. It does not return 0 from `main`. The existing tests all assert `main(...) == 0`, so a test written in that style would fail. A test for this action must use `pytest.raises(SystemExit)` and check `exc.value.code == 0`. The request says "exits with status 0" but does not say whether `main` should return 0 or raise `SystemExit(0)`. Both give process exit status 0 when run through the console script, because the entry point is wrapped in `sys.exit(main())`. They differ for callers and tests that call `main` directly.

**Output format.** The stock `action="version"` accepts a `version=` string and prints it plus a newline to stdout in Python 3.4 and later. Passing `version=__version__` therefore matches "exactly the value followed by a newline". A format such as `greeter 1.4.2` would violate "exactly". The request is unambiguous on this point.

## Proposed acceptance criteria

1. `main(["--version"])` writes exactly `"1.4.2\n"` to stdout and nothing to stderr.
2. The process exit status is 0 for `greeter --version`. The mechanism (return value or `SystemExit(0)`) is chosen per decision 1 below.
3. The printed value is read from `greeter.__version__` at runtime and is not duplicated as a literal in `cli.py`. A mismatch between the literal and the module attribute would then be caught.
4. `--version` does not print the greeting.
5. A new test in `tests/test_cli.py` follows the existing style (typed `capsys` fixture, no new dependencies). It asserts the stdout string, and the exit mechanism chosen in decision 1.
6. Existing tests still pass, and `--name` behavior is unchanged.

## Risks and unconfirmed items

- Reasonable but unconfirmed: the test should compare against `greeter.__version__`, not a hard-coded `"1.4.2"`, so it does not break on each version bump. The request does not say which.
- Reasonable but unconfirmed: `cli.py` will import `from greeter import __version__`. This works with the package layout and has no circular import, because `__init__.py` imports nothing.
- Unresolved and outside the request: `pyproject.toml` and `__version__` duplicate the version. The request does not ask to reconcile them, so this analysis does not recommend doing so.
- I have not run the test suite or confirmed that the package is installed in the environment. The conclusions come from reading the files, not from execution.
- If `--version` is combined with other arguments (`--version --name Ada`), argparse's action fires as soon as it is parsed. The request does not cover this case, and the default behavior is acceptable.

## Open decisions for the requester

1. Whether `main(["--version"])` should return 0, like the existing tests expect, or raise `SystemExit(0)`, as the stock argparse action does. This determines the implementation and the form of the test. The request's wording ("exits with status 0") leans toward `SystemExit(0)`, but the requester has not confirmed it. If the answer is "either is fine", the stock action with a `pytest.raises(SystemExit)` test is the smaller change and could proceed without further input. It is therefore a question to confirm, and it does not block implementation.

No other decision blocks implementation. Since the stock action satisfies every stated requirement, I count no decision that only the requester can make.

## Recommended next action

Proceed with `parser.add_argument("--version", action="version", version=__version__)`. Add one test that calls `main(["--version"])` inside `pytest.raises(SystemExit)`, checks `exc.value.code == 0`, and checks that `capsys.readouterr().out == f"{__version__}\n"`. Run `pytest` to confirm. Mention the `SystemExit` versus return-value choice in the hand-off so the requester can redirect.

OPEN-DECISIONS: 0
