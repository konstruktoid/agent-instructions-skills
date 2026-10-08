I couldn't add the config loader. The Write tool is disabled in this session, so nothing was created or changed. I also couldn't read the skill's reference files, because those reads were denied.

This is the module I would put in `src/ledger/config.py`:

```python
"""Load the ledger configuration from a YAML file named on the command line."""

import argparse
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import yaml

MAX_CONFIG_BYTES = 1_000_000


class ConfigError(Exception):
    """Raised when the configuration file cannot be read or is not valid."""


def load_config(path: Path) -> dict[str, Any]:
    """Read a YAML mapping from path.

    Parsed with ``yaml.safe_load`` so the file can only produce plain data
    types, never arbitrary Python objects. Parse errors report the location
    but not the file content, which may hold credentials.
    """
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_CONFIG_BYTES + 1)
    except OSError as exc:
        msg = f"cannot read config file {path}: {exc.strerror}"
        raise ConfigError(msg) from None
    if len(raw) > MAX_CONFIG_BYTES:
        msg = f"config file {path} exceeds {MAX_CONFIG_BYTES} bytes"
        raise ConfigError(msg)

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}" if mark is not None else ""
        msg = f"invalid YAML in {path}{where}"
        raise ConfigError(msg) from None

    if data is None:
        return {}
    if not isinstance(data, dict):
        msg = f"config file {path} must contain a mapping at the top level"
        raise ConfigError(msg)
    return data


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(description="Ledger service")
    parser.add_argument("--config", type=Path, required=True,
                        help="path to the YAML configuration file")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Load the configuration named on the command line."""
    args = parse_args(argv)
    try:
        load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}")
        return 1
    return 0
```

Security choices in the design:
- **Safe parsing:** it uses `yaml.safe_load`, never `yaml.load`, so a config file can't construct arbitrary Python objects.
- **Size cap:** it reads at most 1 MB, so an oversized or hostile file can't exhaust memory.
- **Shape check:** it requires a top-level mapping, so a malformed file is rejected where it is loaded.
- **Error messages:** they give the path and line number but never the file's content, and `from None` keeps the original exception out of tracebacks.
- **Operator-supplied path:** it is trusted as the operator's choice, so there is no path sandboxing.

I haven't run any of this, and I haven't run `ruff` or `ty`. The workspace has no `pyproject.toml`, so I don't know how the repository runs them or whether `uv` is set up.

`pyyaml` isn't declared anywhere yet, so it needs adding wherever dependencies are managed, and then checking against any vulnerability scanner you use.

If you re-enable Write, or want me to apply it another way, I can add the file, a test in `tests/`, and run the checks. I can also read the skill's reference files if you approve access to that directory.
