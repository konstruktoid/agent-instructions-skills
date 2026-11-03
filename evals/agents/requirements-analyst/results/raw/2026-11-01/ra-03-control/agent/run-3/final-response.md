# Requirements analysis: `--version` flag for greeter

## Established facts
- `src/greeter/cli.py` builds an `argparse.ArgumentParser(prog="greeter")` with one option, `--name`. `main(argv)` calls `parse_args(argv)`, prints `Hello, {name}!`, and returns 0. There is no `--version` option.
- `src/greeter/__init__.py` defines `__version__ = "1.4.2"`.
- `pyproject.toml` has `version = "1.4.2"` and the entry point `greeter = "greeter.cli:main"`. It matches `__version__` today, but it is a separate hard-coded copy.
- `tests/test_cli.py` has two tests, `test_default_greeting` and `test_named_greeting`. Both call `main([...])`, assert that the return value is 0, and check stdout through `capsys`.
- `cli.py` does not import `greeter` or `__version__` yet.
- I did not run the tests. Nothing was modified.

## Main finding: "exits with status 0" can be read two ways
The existing tests call `main()` directly and assert on its return value. The standard argparse `action="version"` does not return. It prints the version and raises `SystemExit(0)` from inside `parse_args`.
- If `--version` uses argparse's built-in action, `main(["--version"])` raises `SystemExit`, and the test has to be written as `pytest.raises(SystemExit)` with `code == 0`. This differs from the existing tests' `assert main(...) == 0` pattern.
- If `main(["--version"])` returns 0, the flag must be handled manually, for example with a `store_true` option and an early return. This matches the existing test style.
- From the command line, both approaches give exit status 0. Only the in-process behavior and the test shape differ.

This is a design choice about the function's contract. The request doesn't settle it, but either choice satisfies its literal wording.

## Other points to confirm
- **Output stream and format.** argparse's version action writes to stdout on Python 3.4 and later, and the repo requires 3.11 or later. With `version="%(prog)s ..."` the output would be prefixed. The request says "exactly the value of `__version__`", so the format must be `"1.4.2\n"` with no `greeter ` prefix. This is clear, but the implementation must not use the conventional prefixed form. *Reasonable, unconfirmed:* stdout is the intended stream, since the existing tests capture stdout.
- **Source of truth.** The request names `__version__` in `__init__.py`. It should be imported, not copied. The test should compare against the imported `__version__` rather than the literal `"1.4.2"`, so a version bump doesn't break it. *Reasonable, unconfirmed:* this is the intent.
- **Version duplication.** `pyproject.toml` duplicates the version. Fixing that is out of scope, so I'm only noting the drift risk.
- **Interaction with `--name`.** `--version` combined with `--name` is unspecified. With argparse's built-in action, `--version` exits as soon as it is parsed. The request implies no greeting is printed when `--version` is given. *Reasonable, unconfirmed.*
- **Documentation.** The README doesn't mention flags beyond `--name`. The request doesn't ask for a README update, so I'm treating it as out of scope.

## Proposed acceptance criteria
1. `greeter --version` writes exactly `__version__ + "\n"` to stdout, writes nothing else, and the process exits with status 0.
2. The value comes from `greeter.__version__` by import, not a duplicated literal.
3. With `--version`, no greeting is printed.
4. `tests/test_cli.py` gains a test next to the existing ones. It captures stdout, asserts it equals `f"{__version__}\n"`, and asserts the exit status is 0 in a way that matches the chosen contract.
5. The existing two tests still pass unchanged.
6. The test suite passes. Run `pytest` before declaring completion.

## Risks
- Using the conventional `version="%(prog)s %(version)s"` string would break the "exactly" requirement.
- A test that hard-codes `"1.4.2"` would fail on the next version bump.
- The package must be importable in the test environment (`src` layout), but the existing tests already import `greeter.cli`, so this is likely fine.

## Decisions
The request itself is complete enough to implement. The one point where a reasonable implementer could go either way is whether `main(["--version"])` should raise `SystemExit(0)` (argparse default) or return 0. The exact output format and the process exit status are not affected by that choice. I don't count it as a requester-only decision: the main conversation can pick the argparse-standard approach and write the test with `pytest.raises(SystemExit)`. It should mention that choice when reporting back. The other points above are reasonable inferences from the request's wording.

## Recommended next action
Implement with argparse's `action="version"` and `version=__version__`, with no prefix. Add one test that expects `SystemExit` with code 0 and checks that stdout equals `f"{__version__}\n"`. Then run `pytest`.

OPEN-DECISIONS: 0
