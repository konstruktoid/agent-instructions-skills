I couldn't save this to a file. Write is disabled in this session, and my reads of the skill's reference files and instruction file were denied. So I haven't run `ruff` or `ty` on it, and I wrote it from general SSRF knowledge instead of the skill's references. The code is below, meant for `src/ledger/fetch.py`.

```python
"""Fetch client-supplied URLs against an allowlist and cache the response bodies."""

import ipaddress
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"api.example.com"})
TIMEOUT_SECONDS = 5
MAX_BODY_BYTES = 1_000_000
CACHE_TTL_SECONDS = 300
MAX_CACHE_ENTRIES = 256

_cache: dict[str, tuple[float, bytes]] = {}


class FetchError(Exception):
    """The URL was rejected or the fetch failed."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so an allowed host cannot bounce us to an internal one."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001, ANN201, PLR0913
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def _validate(url: str) -> str:
    """Return the normalised URL if it is https, allowlisted and publicly routable."""
    parts = urlsplit(url)
    host = parts.hostname
    if parts.scheme != "https" or host is None or parts.username or parts.password:
        raise FetchError("URL must be https, with a host and no credentials")
    if host not in ALLOWED_HOSTS:
        raise FetchError("host is not allowed")
    try:
        port = parts.port or 443
        addresses = {i[4][0] for i in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)}
    except (ValueError, OSError) as exc:
        raise FetchError("host could not be resolved") from exc
    if not addresses or not all(ipaddress.ip_address(a).is_global for a in addresses):
        raise FetchError("host resolves to a non-public address")
    return parts.geturl()


def fetch_cached(url: str) -> bytes:
    """Return the body of an allowlisted https URL, served from cache while fresh."""
    key = _validate(url)
    now = time.monotonic()
    hit = _cache.get(key)
    if hit is not None and now - hit[0] < CACHE_TTL_SECONDS:
        return hit[1]

    request = urllib.request.Request(key, headers={"Accept-Encoding": "identity"})  # noqa: S310 - scheme/host validated above
    try:
        with _opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise FetchError("fetch failed") from exc
    if len(body) > MAX_BODY_BYTES:
        raise FetchError("response too large")

    if len(_cache) >= MAX_CACHE_ENTRIES:
        _cache.pop(min(_cache, key=lambda k: _cache[k][0]))
    _cache[key] = (now, body)
    return body
```

A client-supplied URL is an SSRF risk, so the function limits what it will fetch:

- **Allowlist:** only https URLs with no embedded credentials, and only hosts in `ALLOWED_HOSTS`. `api.example.com` is a placeholder, so replace it with your real hosts.
- **Address check:** the host's resolved addresses must all be public, which blocks loopback, private ranges and cloud metadata addresses.
- **Redirects:** redirects are refused, so an allowed host can't send the request to an internal one.
- **Limits:** the request has a timeout and the body is capped at 1 MB.
- **Cache:** it is keyed on the validated URL, expires after 5 minutes, and holds at most 256 entries so a client can't grow it without bound.
- **Errors:** failures raise `FetchError` with generic messages, so no internal detail reaches the caller.

- **DNS rebinding:** DNS is resolved once for the check and again by `urllib` when it connects. Because the host list is fixed, the remaining risk is small. If you need to close it fully, connect to the validated IP and send the original `Host` header and TLS server name.
- **Threads:** the cache isn't thread-safe. Add a lock if it's called from multiple threads.

If you grant write access, I can save this file and run `uv run ruff check`, `ruff format --check` and `ty check` on it.
