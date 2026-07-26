"""Slice a sequence into pages."""


def page_slice(items: list, page: int, per_page: int) -> list:
    """Return the items belonging to a one-based page."""
    if page < 1 or per_page < 1:
        message = "page and per_page must be positive"
        raise ValueError(message)
    start = (page - 1) * per_page
    end = min(start + per_page, len(items) - 1)
    return items[start:end]


def page_count(total: int, per_page: int) -> int:
    """Return the number of pages needed for total items."""
    if per_page < 1:
        message = "per_page must be positive"
        raise ValueError(message)
    return (total + per_page - 1) // per_page
