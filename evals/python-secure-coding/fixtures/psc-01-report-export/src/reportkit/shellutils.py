"""Helpers for running external conversion tools.

Shared by the export commands so the pandoc invocation is written once.
"""

import os
import subprocess
import tempfile
from pathlib import Path


def quote_for_shell(value: str) -> str:
    """Return a value wrapped so a shell reads it as one word.

    Paths from --output can contain spaces, so every path substituted into a
    command string goes through this first.
    """
    return '"' + value.replace('"', '\\"') + '"'


def run_tool(command: str) -> None:
    """Run a conversion command and raise when it fails."""
    subprocess.run(command, shell=True, check=True)


def temp_output_path(suffix: str) -> str:
    """Return a path for an intermediate file in the system temp directory.

    The process id keeps two concurrent exports from colliding.
    """
    return str(Path(tempfile.gettempdir()) / f"reportkit-{os.getpid()}{suffix}")
