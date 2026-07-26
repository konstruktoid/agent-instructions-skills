"""Tests for paging.slicing."""

import pytest
from paging import page_count, page_slice


@pytest.mark.parametrize(
    ("page", "per_page", "expected"),
    [
        (1, 2, ["a", "b"]),
        (2, 2, ["c", "d"]),
        (1, 3, ["a", "b", "c"]),
    ],
)
def test_page_slice_returns_the_requested_page(letters, page, per_page, expected):
    """A page in the middle of the sequence holds per_page items."""
    assert page_slice(letters, page, per_page) == expected


@pytest.mark.parametrize(
    ("total", "per_page", "expected"),
    [(6, 2, 3), (7, 2, 4), (0, 2, 0)],
)
def test_page_count_rounds_up(total, per_page, expected):
    """A partial final page still counts as a page."""
    assert page_count(total, per_page) == expected


@pytest.mark.parametrize("per_page", [0, -1])
def test_page_slice_rejects_a_non_positive_page_size(letters, per_page):
    """A non-positive page size is a caller error."""
    with pytest.raises(ValueError, match="positive"):
        page_slice(letters, 1, per_page)
