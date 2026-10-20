"""Writers for report data."""

import json


def export_json(rows, path):
    """Write rows, a list of dicts, to path as indented JSON."""
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
