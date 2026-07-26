"""Client that retries a transport call."""

MAX_ATTEMPTS = 3


def get(transport, path: str) -> str:
    """Fetch a path, retrying on transport failure."""
    for _ in range(MAX_ATTEMPTS):
        result = transport(path)
        if result is not None:
            return result
    return ""
