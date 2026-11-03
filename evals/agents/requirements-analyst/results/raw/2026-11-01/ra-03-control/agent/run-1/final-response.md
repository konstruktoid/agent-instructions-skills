## Established facts

- `src/greeter/cli.py` builds an `argparse.ArgumentParser(prog="greeter")` with one option, `--name`. `main(argv)` calls `parse_args(argv)`, prints `Hello, {name}!`, and returns 0.
- `src/greeter/__init__.py` defines `__version__ = "1.4.2"`.
- `pyproject.toml` also hard-codes `version = "1.4.2"`. It is static, not derived from `__init__.py`. The two values match today. The console script is `greeter = "greeter.cli:main"`.
- `tests/test_cli.py` has two tests. Both call `main([...])`, assert that the return value is 0, and assert on `capsys.readouterr().out`. The file imports `pytest` and uses type-annotated fixtures.
- The README has no mention of a version.
- I did not run the tests. They are not needed to establish the above.

## Key finding: "exits with status 0" conflicts with how the tests call `main`

- The existing tests call `main(...)` in-process and check its return value.
- The usual way to add this flag is argparse's `action="version"`. It prints the version and then calls `sys.exit(0)`, which raises `SystemExit`. `main` therefore never returns.
- A test written in the existing style (`assert main(["--version"]) == 0`) would fail. The test would have to use `pytest.raises(SystemExit)` and check `.code == 0`.
- Two implementations satisfy the request:
  1. Use `action="version"`. The test then expects `SystemExit` with code 0. The flag works the same way from the shell.
  2. Handle the flag manually, so `main` prints and returns 0. The test then matches the existing style.
- From the shell, both give exit status 0. They differ in what `main(["--version"])` does for in-process callers.

## Other points to check

- **Output format.** The request says to print "exactly the value of `__version__`" and a newline. That means `1.4.2\n`, with no `greeter ` prefix. argparse's `version=` string is the text printed, so `version=__version__` produces exactly that. A common `"%(prog)s X"` format would violate the request. Newer Python versions print the version to stdout. Python ≥3.11 is required, so stdout is assured.
- **Import.** `cli.py` has no import of the package version yet. It needs `from greeter import __version__`. This is not a circular import, because `__init__.py` imports nothing.
- **Duplicate version.** `pyproject.toml` and `__init__.py` can drift apart. The request names `__init__.py` as the source, so that is the source of truth. Unifying them is outside the request.
- **Test assertion.** The test should assert `out == f"{__version__}\n"` or the literal `"1.4.2\n"`. The literal fails on every version bump, while the imported value cannot catch a wrong source. This choice is minor and the implementer can make it.

## Proposed acceptance criteria

1. `greeter --version` and `python -m greeter.cli --version`, if the module is runnable, write exactly `__version__` plus `\n` to stdout and exit with status 0. The second form is an inference, because `cli.py` has no `__main__` guard.
2. `--version` produces no greeting output and does not need `--name`.
3. Running with no arguments or with `--name` behaves as before, and the two existing tests still pass.
4. A new test in `tests/test_cli.py` covers `--version`. It checks the exact stdout and the exit status 0, using the style that matches the chosen implementation.
5. No other files change, and the version in `pyproject.toml` is left alone.

## Open decisions

The one real choice is the implementation style. It determines whether `main(["--version"])` raises `SystemExit(0)` or returns 0, which in turn decides the shape of the test. The request does not say which to use. The "followed by a newline and exits with status 0" wording fits either. The standard argparse behavior is the lowest-risk reading, and the request would hold under both. I would not treat this as blocking, but the requester can override it. Nothing else needs the requester's input.

**Recommended next action:** Proceed with `action="version", version=__version__`. Write the test with `pytest.raises(SystemExit)`, then check `exc.value.code == 0` and `capsys.readouterr().out == f"{__version__}\n"`. Mention the choice in the handoff. Run `pytest` before reporting completion.

OPEN-DECISIONS: 0
