"""Exporters for a finished report."""

import csv
import io
from importlib.metadata import entry_points


def csv_export(rows: list[dict[str, str]]) -> str:
    """Render rows as CSV with a header line."""
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def legacy_export(rows: list[dict[str, str]]) -> str:
    """Render rows in the tab-separated layout of reportkit 1.x."""
    return "\n".join("\t".join(row.values()) for row in rows)


def exporter(name: str):
    """Return the exporter registered under name."""
    (entry,) = entry_points(group="reportkit.exporters", name=name)
    return entry.load()
