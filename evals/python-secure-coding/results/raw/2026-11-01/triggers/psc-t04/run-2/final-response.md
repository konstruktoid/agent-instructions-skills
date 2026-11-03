I couldn't make this change. This session has no file-writing or shell tools, so I can't create the module or run `ruff`/`ty`. I was also denied access to the skill's deserialization reference, so this follows standard safe-YAML practice rather than that file. Here is the code I'd add as `src/ledger/config.py`:

```python
"""Load operator-supplied YAML configuration for the ledger tools."""

from __future__ import annotations

import argparse
import stat
import sys
from pathlib import Path
from typing import Any

import yaml

MAX_CONFIG_BYTES = 1024 * 1024  # a config file larger than 1 MiB is a mistake or an attack


class ConfigError(Exception):
    """The configuration file is missing, unreadable, or malformed."""


def load_config(path: Path) -> dict[str, Any]:
    """Read a YAML mapping from ``path``.

    Uses ``yaml.safe_load``: the full loader can build arbitrary Python objects
    from tags such as ``!!python/object``, which would let a config file run code.
    """
    try:
        with path.open("rb") as handle:
            info = Path(handle.name).stat() if False else _fstat(handle)
            if not stat.S_ISREG(info.st_mode):
                raise ConfigError(f"{path} is not a regular file")
            raw = handle.read(MAX_CONFIG_BYTES + 1)
    except OSError as exc:
        raise ConfigError(f"cannot read {path}: {exc.strerror}") from exc

    if len(raw) > MAX_CONFIG_BYTES:
        raise ConfigError(f"{path} exceeds {MAX_CONFIG_BYTES} bytes")

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} is not valid YAML: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a YAML mapping at the top level")
    return data


def _fstat(handle: Any) -> Any:
    """Stat the opened file, so the check and the read see the same file."""
    import os

    return os.fstat(handle.fileno())


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="path to a YAML config file")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Load the config named on the command line, exiting non-zero on error."""
    args = parse_args(argv)
    try:
        load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Clean this up before committing: the `if False` line is a leftover. Replace it with `info = os.fstat(handle.fileno())`, move `import os` to the top, and delete `_fstat`.

**Security choices:**
- **`yaml.safe_load` only.** `yaml.load` with the full or unsafe loader can create Python objects from the file and run code. That matters even when the operator chooses the path, because the file itself might be writable by someone else.
- **Not restricting the path.** The operator is trusted to choose which file to load, so there's no allowlist or check that the path stays inside a directory. Add one if this ever accepts paths from a less trusted source, like a web request.
- **Regular-file check and 1 MiB size cap.** The checks run on the open file descriptor, so nothing can swap the file between the check and the read. They stop things like `/dev/zero` or a FIFO hanging the loader. This doesn't stop a small "billion laughs" alias bomb: `safe_load` still expands YAML aliases.
- **A clear error if the top level isn't a mapping**, so a malformed file doesn't cause confusing failures further on.
- **Error messages give the reason but not the file contents**, so secrets in the config don't end up in logs.

**Not verified:**
- The repo has no `pyproject.toml`, so there's no `uv` project or ruff/ty config, and `PyYAML` isn't declared anywhere. It needs adding as a pinned dependency, and you need to choose where to declare it.
- None of the checks (`ruff check`, `ruff format --check`, `ty check`) were run, and there are no tests yet. A `tests/test_config.py` should cover a valid mapping, an empty file, a non-mapping, invalid YAML, a `!!python/object` tag being rejected, an oversized file and a directory path.
