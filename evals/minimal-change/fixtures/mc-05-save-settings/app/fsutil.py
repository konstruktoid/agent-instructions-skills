"""File helpers."""

import os
import tempfile


def atomic_write(path, text):
    """Replace the file at path with text, or leave it untouched if the write fails."""
    directory = os.path.dirname(os.path.abspath(path))
    handle, temporary = tempfile.mkstemp(dir=directory)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    except BaseException:
        os.unlink(temporary)
        raise
