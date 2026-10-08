"""Command-line entry point."""

import argparse
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser."""
    parser = argparse.ArgumentParser(prog="greeter")
    parser.add_argument("--name", default="world", help="who to greet")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command and return its exit status."""
    args = build_parser().parse_args(argv)
    print(f"Hello, {args.name}!")
    return 0
