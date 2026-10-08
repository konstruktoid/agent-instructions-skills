I couldn't write the file or run any checks, so nothing has been saved or verified. The Write tool is disabled in this session. Reads of the skill's instruction and reference files (`instructions/python_coding_instructions.md` and `references/access-control.md`) were also denied. I wrote the function below from general SSRF practice instead of those references. I haven't run `ruff` or `ty` on it, so the `noqa` markers and the `redirect_request` signature are unchecked.

This is meant for `src/ledger/fetch.py`:

```python
"""Fetch client-supplied URLs from an allowlist of hosts and cache the bodies."""

import ipaddress
import socket
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"api.example.com"})
MAX_BODY_BYTES = 1_000_000
MAX_CACHE_ENTRIES = 256
TIMEOUT_SECONDS = 5

_cache: dict[str, bytes] = {}


class FetchError(Exception):
    """Raised when a URL is rejected or cannot be fetched."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so a validated host cannot bounce to an internal one."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201, PLR0913
        return None


def _validate(url: str) -> str:
    """Return the normalized URL, or raise FetchError if it is not allowed."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise FetchError("only https URLs are allowed")
    if parts.username is not None or parts.password is not None:
        raise FetchError("credentials in URLs are not allowed")
    host = (parts.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise FetchError("host is not allowed")
    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, parts.port or 443)}
    except socket.gaierror as exc:
        raise FetchError("host could not be resolved") from exc
    if not all(ipaddress.ip_address(addr).is_global for addr in addresses):
        raise FetchError("host resolves to a non-public address")
    return parts.geturl()


def fetch_cached(url: str) -> bytes:
    """Return the body of an allowlisted https URL, caching it by URL.

    The URL is client-controlled, so it is checked against ALLOWED_HOSTS and
    must resolve to public addresses only (SSRF guard). Redirects are refused,
    the response is size-capped, and the cache is bounded.
    """
    key = _validate(url)
    if key in _cache:
        return _cache[key]

    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(key, method="GET")  # noqa: S310 - https and host allowlist enforced by _validate
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise FetchError("fetch failed") from exc
    if len(body) > MAX_BODY_BYTES:
        raise FetchError("response too large")

    if len(_cache) >= MAX_CACHE_ENTRIES:
        _cache.pop(next(iter(_cache)))
    _cache[key] = body
    return body
```

Security decisions:
- **SSRF:** The client controls the URL, so it must be `https` and its host must be in `ALLOWED_HOSTS`. You'll need to fill that set in; it only contains a placeholder.
- **Internal addresses:** The host must also resolve only to public addresses. This is a second check on top of the allowlist, not a replacement for it.
- **Redirects:** They are refused, so an allowed host can't send the request on to an internal one.
- **Limits:** There is a timeout, a response size cap, and a cache capped at 256 entries, so a client can't exhaust memory.
- **Errors:** They are generic, so internal details aren't echoed back to the client.

Known limits:
- **DNS rebinding:** The resolve check and the actual connection are separate lookups, so a rebinding attack could still get through. Pinning the connection to the validated IP would close this.
- **Cache expiry:** The cache is in-process and has no expiry. Evicting the oldest entry keeps it bounded but won't refresh stale bodies. It also isn't thread-safe, so add a lock if this runs under threads.
- **Cache scope:** It is keyed by URL only. That's fine for public content, but don't use it for responses that vary by caller.

If you re-enable Write and read access to the skill files, I'll save the file, check it against the references, and run `uv run ruff check`, `uv run ruff format --check` and `uv run ty check`. I can also add tests.
