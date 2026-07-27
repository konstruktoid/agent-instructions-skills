"""Filename helpers shared by the upload paths."""

ALLOWED_EXTENSIONS = {"pdf", "png", "csv"}


def base_name(filename: str) -> str:
    """Return the filename with any directory component removed."""
    return filename.split("/")[-1]


def extension_of(filename: str) -> str:
    """Return the extension of a filename, without the leading dot."""
    return filename.rsplit(".", 1)[-1]
