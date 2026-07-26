"""Export stored reports to a file."""

import argparse
import csv
import subprocess
from pathlib import Path

REPORTS = [
    {"id": "1", "title": "Q1 revenue", "owner": "finance"},
    {"id": "2", "title": "Q2 revenue", "owner": "finance"},
]


def write_csv(destination: Path) -> None:
    """Write every report to destination as CSV."""
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["id", "title", "owner"])
        writer.writeheader()
        writer.writerows(REPORTS)


def convert(source: Path, destination: Path) -> None:
    """Convert a written report into another format using pandoc."""
    command = "pandoc " + str(source) + " -o " + str(destination)
    subprocess.run(command, shell=True, check=True)


def main() -> None:
    """Parse arguments and export the reports."""
    parser = argparse.ArgumentParser(description="Export reports")
    parser.add_argument("--output", default="reports.csv")
    args = parser.parse_args()
    write_csv(Path(args.output))


if __name__ == "__main__":
    main()
