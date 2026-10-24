I couldn't create the file. This session only has read and search tools, with no way to write or edit files or run a shell. I also couldn't run the skill's checks (`ruff check`, `ruff format --check`, `ty check`), and my request to read the skill's deserialization reference was declined. So the code below is untested. It's meant for `src/ledger/config.py`, styled like `src/ledger/client.py`:

```python
"""Load operator-supplied YAML configuration."""

import argparse
from pathlib import Path
from typing import Any

import yaml

MAX_CONFIG_BYTES = 1_000_000


class ConfigError(Exception):
    """Raised when a config file cannot be read or is malformed."""


def load_config(path: Path) -> dict[str, Any]:
    """Read a YAML file and return its top-level mapping.

    Uses yaml.safe_load so the file can only produce plain data types,
    never arbitrary Python objects.
    """
    try:
        if path.stat().st_size > MAX_CONFIG_BYTES:
            msg = f"config file exceeds {MAX_CONFIG_BYTES} bytes: {path}"
            raise ConfigError(msg)
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        msg = f"cannot read config file {path}: {exc.strerror}"
        raise ConfigError(msg) from exc
    except yaml.YAMLError as exc:
        msg = f"invalid YAML in config file {path}"
        raise ConfigError(msg) from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        msg = f"config file must contain a mapping at top level: {path}"
        raise ConfigError(msg)
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command line for the config file path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="Path to YAML config file.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> dict[str, Any]:
    """Load the config named on the command line."""
    args = parse_args(argv)
    try:
        return load_config(args.config)
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc
```

The main security choices:
- **`yaml.safe_load`, not `yaml.load`.** With `yaml.load`, a config file could create arbitrary Python objects and run code. `safe_load` only returns plain data like dicts, lists, strings and numbers.
- **Top-level shape check.** The file must contain a mapping at the top level. Otherwise a list or a bare string would only fail later, somewhere unrelated in the code. An empty file loads as `{}`.
- **Size cap.** Files over 1 MB are rejected before parsing.
- **No path restriction.** The operator supplies the path, so the loader reads whatever file they name with their own permissions. If this ever runs with more privileges than the operator has, or takes a path from a less trusted source, it should only accept files inside an allowed config directory.
- **Errors.** File and YAML errors come back as a one-line `ConfigError` with no traceback or file contents. `main` turns that into a clean exit.

You'll also need to handle the dependency. The workspace has no `pyproject.toml`, so PyYAML isn't declared anywhere. Add it with `uv add pyyaml` (plus `uv add --dev types-PyYAML` for `ty`), or create a project first if there isn't one. Run your vulnerability scanner, if you have one, after adding it.

Once you've saved the file, run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`. Those checks need a `pyproject.toml`, so add PyYAML first. I can also write a test like `tests/test_balance.py`.
