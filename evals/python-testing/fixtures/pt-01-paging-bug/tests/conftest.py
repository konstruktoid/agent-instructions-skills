"""Shared fixtures for the paging tests."""

import pytest


@pytest.fixture
def letters() -> list:
    """Return a predictable sequence to page over."""
    return ["a", "b", "c", "d", "e", "f"]
