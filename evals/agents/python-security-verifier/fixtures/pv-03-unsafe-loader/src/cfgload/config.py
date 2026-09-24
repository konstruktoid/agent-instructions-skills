"""Load a tenant's uploaded YAML configuration."""

from pathlib import Path

import yaml


def load_config(path: Path) -> dict[str, object]:
    """Parse the YAML file at path and return its top-level mapping."""
    with path.open(encoding="utf-8") as handle:
        return yaml.load(handle, Loader=yaml.Loader)
