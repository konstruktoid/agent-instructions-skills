## Established facts
- `src/greeter/cli.py` (read in full) has `build_parser()`, an argparse parser with prog `greeter` and a single `--name` option. `main(argv)` parses the arguments, prints `Hello, {name}!` and returns 0. It has no version handling.
- `src/greeter/__init__.py` defines `__version__ = "1.4.2"`.
- `pyproject.toml` also hardcodes `version = "1.4.2"`. Nothing links it to `__version__`; the two values are separate and currently agree. The project requires Python 3.11 or later. The console script is `greeter = greeter.cli:main`.
- `tests/test_cli.py` has two tests, `test_default_greeting` and `test_named_greeting`. Both call `main([...])`, assert that it returns 0, and compare `capsys.readouterr().out` to the exact expected string.
- The README has no mention of version or exit behaviour.

## Key observation
The existing tests assume `main()` returns 0. argparse's `action="version"` does not return. It prints and then raises `SystemExit(0)`. So the new test cannot copy the `assert main(...) == 0` pattern. It must use `pytest.raises(SystemExit)` and check `excinfo.value.code == 0`. The alternative is for `main` to handle the flag itself and return 0.

## Proposed acceptance criteria
1. `main(["--version"])` writes exactly `"1.4.2\n"` to stdout, which is `__version__` plus one newline. It writes nothing to stderr and prints no greeting.
2. The process exit status is 0. This holds when the console script `greeter --version` runs, and the test checks it either as `SystemExit.code == 0` or as a return value of 0.
3. The printed value comes from `greeter.__version__`, not a copy of the literal. Changing `__version__` changes the output.
4. A new test in `tests/test_cli.py` covers 1 and 2, and the test file imports `__version__` from `greeter` so it does not hardcode `"1.4.2"`.
5. The existing two tests still pass and `--name` behaviour is unchanged.

## Assumptions
- Confirmed: argparse in Python 3.11 or later writes the version to stdout and exits 0. The text is `__version__` plus a newline, with no `prog` prefix, as long as `version=` is the bare string. This matches the "exactly" wording.
- Reasonable but unconfirmed: "exits with status 0" means a process-level exit, so a `SystemExit(0)` is acceptable and `main` need not return.
- Reasonable but unconfirmed: the test should assert against `__version__` imported from the package. A literal would break on every version bump.

## Unresolved decisions
These are minor. The request is mostly specified, and the first two have a sensible default.
- **Implementation mechanism:** use argparse `action="version"`, which raises `SystemExit`, or handle the flag manually so `main` returns 0 like the other paths. This does not change the observable behaviour for the CLI. It does change how the test is written. I recommend the argparse action as the default.
- **Combined flags:** the behaviour of `--version --name X` is not specified. argparse's action exits as soon as it sees the flag, so the version is printed and no greeting appears. I recommend accepting that.
- **Version drift:** `pyproject.toml` and `__version__` are duplicated. The request names `__version__` as the source, so the flag does not depend on `pyproject.toml`. Unifying them is out of scope, and I am not proposing it.
- I found no short `-V` alias requested, and I would not add one.

None of these block implementation, because each has a reasonable default consistent with the request.

## Risks
- If the test copies the existing pattern (`assert main([...]) == 0`), it will fail with `SystemExit`.
- Hardcoding `"1.4.2"` in either the code or the test would silently drift when the version changes.

## Recommended next action
Proceed with the argparse `version` action using `__version__` imported from `greeter`, plus a `pytest.raises(SystemExit)` test that checks stdout equals `f"{__version__}\n"` and the exit code is 0. Before implementing, check `.agent-standards/instructions/python_coding_instructions.md` and `minimal_change_instructions.md` for style conventions. I did not read them.

OPEN-DECISIONS: 0
