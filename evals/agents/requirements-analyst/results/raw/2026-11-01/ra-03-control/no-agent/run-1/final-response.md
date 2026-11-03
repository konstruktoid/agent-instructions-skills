**Analysis only. I changed no files.**

## What the repository establishes

- **`src/greeter/cli.py`**
  - `build_parser()` creates `argparse.ArgumentParser(prog="greeter")` with one option, `--name` (default `"world"`).
  - `main(argv=None) -> int` parses the arguments, prints `Hello, {name}!` and returns `0`.
  - Nothing in the module imports `greeter` or `__version__` yet.
- **`src/greeter/__init__.py`** defines `__version__ = "1.4.2"`.
- **`pyproject.toml`**
  - It has a separate, hardcoded `version = "1.4.2"`. The two values match today, but nothing keeps them in sync.
  - The console script is `greeter = "greeter.cli:main"`. The installed command runs `sys.exit(main())`, so a return value of `0` gives exit status 0.
- **`tests/test_cli.py`**
  - It has two tests, `test_default_greeting` and `test_named_greeting`.
  - Both call `main([...])`, assert that the return value is `0`, and compare `capsys.readouterr().out` exactly.
  - New tests should follow that pattern: type-annotated, using `pytest.CaptureFixture[str]`.

## What the request fixes

- The flag name is `--version`.
- The output is exactly `__version__` plus a newline, so no `greeter ` prefix.
- The exit status is 0.
- The test goes in `tests/test_cli.py`.

## Implementation notes (not requester decisions)

- **Exit mechanism.** `argparse`'s built-in `action="version"` fits the request.
  - With `version=__version__` it prints the bare value plus a newline to stdout, then raises `SystemExit(0)`. `1.4.2` contains no `%` characters, so argparse's format expansion does not alter it.
  - A consequence is that `main(["--version"])` does not return `0`. It raises `SystemExit`, unlike the existing tests. The test should use `pytest.raises(SystemExit)`, check `exc.value.code == 0`, and then check `capsys.readouterr().out == f"{__version__}\n"`.
  - The alternative is a manual check that prints the version and returns `0`. That matches the existing test style but bypasses argparse's help listing and its handling of the flag.
  - Both options meet the stated requirements, so this is a design choice for the implementer.
- **Test should compare to `__version__`.** It should import `__version__` rather than hardcode `"1.4.2"`. That way it won't break when the version is bumped.
- **Duplicate version in `pyproject.toml`.** It is outside this request and I would leave it alone. It is a possible future drift risk.
- **Interaction with the required `--name`.** `--name` is optional, so `--version` alone needs no extra arguments. With argparse's version action, the flag exits before any greeting is printed.

## What has to be settled first

Nothing that only the requester can decide. The behavior, output format, exit status and test location are all specified, and the remaining choices are implementation details.

OPEN-DECISIONS: 0
