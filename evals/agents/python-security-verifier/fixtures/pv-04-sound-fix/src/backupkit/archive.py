"""Archive a directory with tar."""

import os
from pathlib import Path


def archive(src: Path, dest: Path) -> None:
    """Write a gzip-compressed tar archive of src to dest."""
    os.system("tar -czf " + str(dest) + " " + str(src))
