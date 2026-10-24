I couldn't create the file or run anything. This session only gave me read and search tools, with no write, edit or shell access. So the code below is untested: I haven't run `ruff`, `ty` or any tests on it. There's also no `pyproject.toml` or `uv` setup in the workspace to run them through.

The project currently has `src/ledger/balance.py` and `client.py`, and nothing that reads config yet. Here's the proposed **`src/ledger/config.py`**:

```python
"""Load ledger configuration from an operator-supplied YAML file."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

MAX_CONFIG_BYTES = 1_000_000


class ConfigError(Exception):
    """Raised when the configuration file cannot be read or parsed."""


def load_config(path: Path) -> dict[str, Any]:
    """Read ``path`` and return its top-level YAML mapping.

    Uses ``yaml.safe_load`` so tags such as ``!!python/object`` cannot
    construct arbitrary Python objects from the file.
    """
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_CONFIG_BYTES + 1)
    except OSError as exc:
        msg = f"cannot read config file {path}: {exc.strerror}"
        raise ConfigError(msg) from exc
    if len(raw) > MAX_CONFIG_BYTES:
        msg = f"config file {path} exceeds {MAX_CONFIG_BYTES} bytes"
        raise ConfigError(msg)

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        # Report only the position: the parser's message can echo file
        # content, which may include credentials.
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}" if mark is not None else ""
        msg = f"invalid YAML in {path}{where}"
        raise ConfigError(msg) from None

    if not isinstance(data, dict):
        msg = f"config file {path} must contain a YAML mapping at the top level"
        raise ConfigError(msg)
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Ledger")
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="path to the YAML configuration file",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: load the configuration named on the command line."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}")  # noqa: T201 - CLI error output
        return 1
    # Hand ``config`` to the application here.
    _ = config
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Security choices:**
- **`yaml.safe_load`, never `yaml.load`:** without it, a config file could run arbitrary code using tags like `!!python/object/apply`.
- **Size cap:** the loader reads at most 1 MB plus one byte from the open file and rejects anything bigger. Measuring what it actually read, rather than checking the size first and reading later, avoids a race if the file changes in between.
- **Top-level mapping required:** a scalar, list or empty file fails at load time instead of surfacing later as an `AttributeError` somewhere else.
- **Error messages hide file content:** a YAML parse error reports only the line number, because the parser's own message can quote the file, and config files often hold credentials.
- **No restriction on which path is allowed:** the path comes from the operator who launches the process and already has shell access, so a traversal check would add nothing. If this path ever comes from a request or other untrusted input instead, that would need to change.

**Before merging:**
1. Add `pyyaml` (and `types-PyYAML` for `ty`) as dependencies, and run a vulnerability check such as `uv audit`. There's currently no `pyproject.toml` to add them to.
2. Run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
3. Add tests to `tests/` covering:
   - a valid file
   - a non-mapping file
   - a malformed file
   - an oversized file
   - a missing path
   - a file containing a `!!python/object` tag, which must fail rather than build the object

If you give me write and shell access, I can create the file, add the tests and run the checks.
