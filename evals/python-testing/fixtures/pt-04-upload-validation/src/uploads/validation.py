"""Validate an uploaded file before it is stored."""

from uploads.naming import base_name

MAX_BYTES = 5 * 1024 * 1024


class UploadRejected(Exception):
    """Raised when an upload does not meet the storage rules."""


def validate_upload(filename: str, size: int) -> str:
    """Check an upload and return the name it should be stored under."""
    if size > MAX_BYTES:
        message = "upload is too large"
        raise UploadRejected(message)
    return base_name(filename)
