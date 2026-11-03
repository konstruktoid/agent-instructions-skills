**Analysis (no files changed)**

**What the repository establishes**
- `src/greeter/cli.py` has `build_parser()`, which builds an `argparse.ArgumentParser(prog="greeter")` with one option, `--name` (default `"world"`). `main(argv=None) -> int` parses the arguments, prints `Hello, {name}!` and returns 0.
- `src/greeter/__init__.py` defines `__version__ = "1.4.2"`. `pyproject.toml` hardcodes the same `1.4.2` separately, and `greeter = "greeter.cli:main"` is the console script.
- `tests/test_cli.py` has two tests, `test_default_greeting` and `test_named_greeting`. Both call `main([...])`, assert on the return value of 0, and check stdout with `capsys`.
- `cli.py` doesn't import `greeter` yet. There is no existing `--version` handling.

**What the request implies**
- The natural fit is `parser.add_argument("--version", action="version", version=__version__)`, with `from greeter import __version__` in `cli.py`.
- On Python 3.11 or later (the project's minimum), argparse's version action writes to stdout, appends a newline, and exits 0. That matches "exactly the value followed by a newline".
- The version string goes through `%`-formatting, so a `%` in the version would be a problem. `1.4.2` is fine.
- That action raises `SystemExit(0)` instead of returning from `main`. The new test therefore can't use the existing `assert main([...]) == 0` pattern. It needs `pytest.raises(SystemExit)` and a check that `exc.value.code == 0`. It should also assert that `capsys.readouterr().out == f"{__version__}\n"`, importing `__version__` instead of hardcoding `"1.4.2"`.
- Through the console script, the exit status is 0 either way.

**What is left undecided**
- A `-V` short alias, and the behavior when `--version` is combined with other arguments such as `--name`. The request doesn't mention either. argparse exits at `--version` and ignores the rest, and I'd assume no alias. These are low-stakes defaults and don't need the requester.
- `__version__` and the `pyproject.toml` version are duplicated and could drift. The request names `__init__.py` as the source, so this is out of scope. It's worth mentioning but doesn't block anything.

**What has to be settled first**
Nothing blocks implementation. The request specifies the output, the exit status, the source of the value and the test location. The points above have reasonable defaults.

OPEN-DECISIONS: 0
