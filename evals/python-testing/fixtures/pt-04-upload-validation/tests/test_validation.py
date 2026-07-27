"""Tests for uploads.validation."""

import pytest

from uploads import UploadRejected, validate_upload


def test_a_small_upload_is_accepted():
    """An upload under the size limit is returned unchanged."""
    assert validate_upload("report.pdf", 1024) == "report.pdf"


def test_an_oversized_upload_is_rejected():
    """An upload over the size limit is refused."""
    with pytest.raises(UploadRejected, match="too large"):
        validate_upload("report.pdf", 50 * 1024 * 1024)
