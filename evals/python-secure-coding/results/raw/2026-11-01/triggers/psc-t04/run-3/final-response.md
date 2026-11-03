I couldn't add the file myself. I only have read and search tools in this session, with no way to write or edit files or run a shell. The code below is the proposed `src/ledger/config.py` for you to paste in. Because I couldn't run anything, it has **not** been checked with `ruff`, `ty` or tests. My permission request to read the skill's notes on unsafe YAML loading was also denied, so this follows general safe-loading practice instead.

### `src/ledger/config.py`

```python
"""Load operator-supplied YAML configuration for the ledger tools."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

# Config files are small; refuse anything larger so a wrong path (a log,
# a device, a huge dump) can't exhaust memory before parsing even starts.
MAX_CONFIG_BYTES = 1024 * 1024


class ConfigError(Exception):
    """Raised when the config file cannot be read or is not a valid config."""


def load_config(path: Path) -> dict[str, Any]:
    """Read a YAML config file and return its top-level mapping.

    Uses ``yaml.safe_load``, which builds only plain types (dict, list, str,
    int, ...). ``yaml.load`` with the default or unsafe loaders can build
    arbitrary Python objects from tags like ``!!python/object/apply``, which
    turns a config file into code execution.

    Raises:
        ConfigError: if the file is missing, not a regular file, too large,
            not valid YAML, or does not contain a mapping at the top level.
    """
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        msg = f"config path is not a regular file: {resolved}"
        raise ConfigError(msg)

    try:
        with resolved.open("rb") as fh:
            raw = fh.read(MAX_CONFIG_BYTES + 1)
    except OSError as exc:
        msg = f"cannot read config file {resolved}: {exc.strerror}"
        raise ConfigError(msg) from exc

    if len(raw) > MAX_CONFIG_BYTES:
        msg = f"config file exceeds {MAX_CONFIG_BYTES} bytes: {resolved}"
        raise ConfigError(msg)

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        # Report only the position, never the file contents: config files
        # often hold credentials, and this message ends up on stderr/logs.
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        msg = f"invalid YAML in {resolved}{where}"
        raise ConfigError(msg) from None

    if data is None:
        return {}
    if not isinstance(data, dict):
        msg = f"config must be a mapping at the top level, got {type(data).__name__}"
        raise ConfigError(msg)
    return data


def build_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Ledger tool")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        required=True,
        help="path to the YAML configuration file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, load the config, and return a process exit code."""
    args = build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    # Hand `config` to the rest of the application here.
    _ = config
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Suggested test, `tests/test_config.py`

```python
"""Tests for the YAML config loader."""

from pathlib import Path

import pytest

from ledger.config import MAX_CONFIG_BYTES, ConfigError, load_config


def test_loads_mapping(tmp_path: Path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text("currency: EUR\nprecision: 2\n")
    assert load_config(cfg) == {"currency": "EUR", "precision": 2}


def test_rejects_python_object_tags(tmp_path: Path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text("x: !!python/object/apply:os.system ['true']\n")
    with pytest.raises(ConfigError):
        load_config(cfg)


@pytest.mark.parametrize("body", ["- a\n- b\n", "just a string\n"])
def test_rejects_non_mapping(tmp_path: Path, body: str) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text(body)
    with pytest.raises(ConfigError, match="mapping"):
        load_config(cfg)


def test_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="regular file"):
        load_config(tmp_path)


def test_rejects_oversized(tmp_path: Path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_bytes(b"#" * (MAX_CONFIG_BYTES + 1))
    with pytest.raises(ConfigError, match="exceeds"):
        load_config(cfg)
```

### Security choices
- **`yaml.safe_load` only.** With PyYAML's unsafe loaders, a single tagged line in the config file can run a shell command. The second test checks that this is rejected.
- **No restriction on which directories the path can point to.** The operator who supplies the path already controls the process, so limiting directories would only get in the way. If this path ever comes from a less trusted source, such as a web request, it would need checking against an allowed base directory.
- **Only regular files under 1 MiB are read.** This stops a mistyped path to a device, pipe or large file from hanging the tool or using up memory.
- **Error messages never include the file's contents.** A YAML error only reports the line and column, because config files often hold credentials.
- **Known gap:** `safe_load` still expands YAML aliases, so a small file built to multiply itself through repeated references (a "billion laughs" file) can use a lot of memory. If config files can come from people who aren't trusted operators, add a limit on aliases or use a YAML parser that has one.

### Before merging
1. **PyYAML needs to be declared as a dependency.** There's no `pyproject.toml` in the workspace, so nothing currently declares it. Add `pyyaml` with a version floor, plus `pytest` for the tests.
2. Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check` and `uv run pytest`. None of them have been run on this code.
3. The `src/` layout means the tests need the package installed, for example with `uv sync`, or `pythonpath = ["src"]` in the pytest config.

If you give me write and shell access, I can add the files, set up `pyproject.toml` and run the checks until they pass.
