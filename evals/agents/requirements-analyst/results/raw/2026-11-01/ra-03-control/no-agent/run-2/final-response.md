## Analysis: add `--version` to greeter

I didn't change any files.

### What the repository establishes

- **`src/greeter/cli.py`**
  - `build_parser()` returns an `argparse.ArgumentParser(prog="greeter")` with one option, `--name`, which defaults to `"world"`.
  - `main(argv=None) -> int` parses the arguments, prints `Hello, {name}!` and returns 0.
  - It has no `--version` option today.
  - `pyproject.toml` registers the console script as `greeter = "greeter.cli:main"`.
- **`src/greeter/__init__.py`**: `__version__ = "1.4.2"`.
- **`pyproject.toml`**: it also hardcodes `version = "1.4.2"`. The two values agree now, but nothing keeps them in sync. The request names `__init__.py` as the source, so I'd use that and leave `pyproject.toml` alone.
- **`tests/test_cli.py`**: two tests, `test_default_greeting` and `test_named_greeting`. Both call `main([...])`, assert the return value is 0, and compare `capsys.readouterr().out` to the exact output.

### Implementation notes (not open questions)

- **Mechanism:** `parser.add_argument("--version", action="version", version=__version__)` does what is asked. On Python 3.11 or later, which `requires-python` guarantees, argparse writes the version string plus a newline to stdout. It then exits with status 0.
- **No `prog` prefix:** the output is exactly `1.4.2\n` as long as the `version=` string doesn't contain `%(prog)s`.
- **Test shape:** the argparse action calls `sys.exit(0)`, so `main(["--version"])` raises `SystemExit` instead of returning 0. The new test can't copy the `assert main(...) == 0` pattern of the existing tests.
  - It should use `pytest.raises(SystemExit)` and check `excinfo.value.code == 0`.
  - It should compare `capsys.readouterr().out` to `f"{__version__}\n"`, importing `__version__` from `greeter` rather than hardcoding `"1.4.2"`.
- **Import:** `cli.py` needs `from greeter import __version__`. There's no circular import, because `__init__.py` imports nothing.
- **Help text:** `--version` will also show up in `--help`. That is standard and harmless.

### What the request leaves undecided

Nothing blocks implementation. The behavior, source of truth, output format, exit status and test location are all specified. The two edge cases, the `SystemExit` handling and the `pyproject.toml` duplication, have clear defaults that follow from the request's wording.

### What has to be settled first

Nothing from the requester. If they want the version kept in sync with `pyproject.toml` (for example through dynamic versioning), that would be a separate request.

OPEN-DECISIONS: 0
