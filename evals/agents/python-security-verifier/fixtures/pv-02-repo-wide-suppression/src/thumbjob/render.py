"""Render thumbnails by calling ImageMagick."""

import subprocess
from pathlib import Path


def make_thumbnail(source: Path, size: int) -> Path:
    """Write a square thumbnail beside source and return its path."""
    target = source.with_suffix(".thumb.png")
    subprocess.run(f"convert {source} -resize {size}x{size} {target}", shell=True, check=True)
    return target
