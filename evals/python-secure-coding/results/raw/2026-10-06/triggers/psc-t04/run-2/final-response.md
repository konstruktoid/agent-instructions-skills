I couldn't add the config loader. Write and Bash are disabled in this session, so I created no files and ran no checks. The two skill reference files I tried to read (the deserialization guidance and the ruff/ty baseline) were also blocked by permissions.

Below is the code I intended to add. Nothing has been linted, type-checked or tested.

**`src/ledger/config.py`**
```python
"""Load the ledger configuration from a YAML file named on the command line."""

import argparse
from pathlib import Path

import yaml

MAX_CONFIG_BYTES = 1_000_000


class ConfigError(Exception):
    """Raised when the configuration file cannot be used."""


def load_config(path: Path) -> dict:
    """Read a YAML mapping from path.

    The path is operator-supplied, but the file content is parsed with
    ``yaml.safe_load`` so it can only produce plain data, never arbitrary
    Python objects. Size is capped before reading.
    """
    try:
        if not path.is_file():
            raise ConfigError(f"config path is not a regular file: {path}")
        if path.stat().st_size > MAX_CONFIG_BYTES:
            raise ConfigError(f"config file exceeds {MAX_CONFIG_BYTES} bytes")
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        # Report the failure type only; parser messages can echo file content,
        # which may contain credentials.
        raise ConfigError(f"cannot read config {path}: {type(exc).__name__}") from None
    if not isinstance(data, dict):
        raise ConfigError("config top level must be a mapping")
    return data


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Ledger tool")
    parser.add_argument("--config", type=Path, required=True, help="path to YAML config")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> dict:
    """Load the config named by --config."""
    return load_config(parse_args(argv).config)
```

**Design choices**
- **Safe parsing:** `yaml.safe_load` only builds plain data, so a file with `!!python/object` tags can't run code.
- **Operator path:** it is trusted as a location but still checked: it must be a regular file and no larger than 1 MB.
- **Error messages:** failures report only the exception type. PyYAML messages can echo file content, which may hold credentials.
- **Top-level check:** the top level must be a mapping, so callers don't get a list or `None`.

**Before this is usable**
- **Dependency:** the repo has no `pyproject.toml`, so PyYAML isn't declared anywhere. Add it, pinned, and run your vulnerability scanner.
- **Tests:** I also planned `tests/test_config.py`. It would cover a valid mapping, rejection of a Python-object tag, a non-mapping top level, and a missing file.
- **Checks:** run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` before merging.

If you re-enable Write and Bash, or grant read access to the skill's plugin directory, I'll create the files and run the checks.
