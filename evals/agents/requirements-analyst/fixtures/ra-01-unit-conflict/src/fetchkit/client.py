"""The request function every batch job calls."""

import urllib.request

from . import config


def get(url: str) -> bytes:
    """Return the body of url, giving up after the configured timeout."""
    last_error: Exception | None = None
    for _ in range(config.RETRIES + 1):
        try:
            with urllib.request.urlopen(url, timeout=config.TIMEOUT_MS / 1000) as response:
                return response.read()
        except OSError as error:
            last_error = error
    raise RuntimeError(f"giving up on {url}") from last_error
