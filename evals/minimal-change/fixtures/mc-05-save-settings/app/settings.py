"""Application settings."""

import json

DEFAULTS = {"theme": "light", "page_size": 25}


def load_settings(path):
    """Return the settings stored at path, with defaults for anything missing."""
    with open(path, encoding="utf-8") as handle:
        return {**DEFAULTS, **json.load(handle)}
