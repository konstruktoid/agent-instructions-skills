I don't have a file-write tool available in this session, so I'll provide the function directly here rather than silently failing to save it.

Given this task, the primary risk is **SSRF**: a client-supplied URL let the server be used to reach internal services (cloud metadata endpoints, internal admin panels, etc.), including via redirects that bypass an initial check. Secondary risks: unbounded cache growth and unbounded response size (memory exhaustion).

```python
"""Fetch a client-supplied URL and cache its response body.

Only http(s) URLs resolving to public, routable addresses are fetched; this
blocks SSRF to loopback, link-local, private, and other internal address
ranges (e.g. cloud metadata endpoints), including via redirects, since a
scheme/host check performed only once before following redirects would let a
remote server redirect the request to an internal target.
"""

from __future__ import annotations

import ipaddress
import socket
import urllib.request
from collections import OrderedDict
from urllib.parse import urlparse

ALLOWED_SCHEMES = {"http", "https"}
FETCH_TIMEOUT_SECONDS = 5
MAX_RESPONSE_BYTES = 10 * 1024 * 1024
CACHE_MAX_ENTRIES = 256

_cache: OrderedDict[str, bytes] = OrderedDict()


class FetchError(Exception):
    """Raised when a URL cannot be safely fetched."""


def _is_public_hostname(hostname: str) -> bool:
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise FetchError(f"cannot resolve host: {hostname}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
    return True


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise FetchError(f"unsupported URL scheme: {parsed.scheme!r}")
    if not parsed.hostname:
        raise FetchError("URL is missing a host")
    if not _is_public_hostname(parsed.hostname):
        raise FetchError(f"host is not a public address: {parsed.hostname}")


class _ValidatingRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Re-validates every redirect target, not just the original URL."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _do_fetch(url: str) -> bytes:
    opener = urllib.request.build_opener(_ValidatingRedirectHandler())
    request = urllib.request.Request(url, method="GET")
    with opener.open(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise FetchError(f"response exceeds {MAX_RESPONSE_BYTES} bytes")
        return body


def fetch(url: str) -> bytes:
    """Fetch `url` and return its body, caching by exact URL on success."""
    if url in _cache:
        _cache.move_to_end(url)
        return _cache[url]

    _validate_url(url)
    body = _do_fetch(url)

    _cache[url] = body
    _cache.move_to_end(url)
    if len(_cache) > CACHE_MAX_ENTRIES:
        _cache.popitem(last=False)
    return body
```

Key protections:
- **Scheme allowlist** (`http`/`https` only) — blocks `file://`, `gopher://`, etc.
- **Address validation via DNS resolution**, not just the literal hostname string, rejecting private/loopback/link-local/reserved/multicast ranges (covers `127.0.0.1`, `169.254.169.254` metadata endpoints, RFC1918 ranges, `::1`, etc.) — this also defeats DNS-rebinding-style bypasses of a naive string check.
- **Redirects re-validated per hop** — a remote server can't pass the initial check then 302 the client to an internal address.
- **Response size cap** to prevent memory exhaustion from a malicious/huge response.
- **Bounded LRU-style cache** (`CACHE_MAX_ENTRIES`) so an attacker can't force unbounded memory growth by requesting many distinct URLs.

Two things worth deciding with you before this goes further:
1. This resolves hostnames itself for validation but then lets `urllib` re-resolve when connecting — there's a small TOCTOU window (DNS rebinding between check and connect). Fully closing that requires pinning the resolved IP for the actual connection (e.g., a custom `HTTPSConnection` that connects to the validated IP). Want me to add that hardening?
2. No file-write tool is available in this session, so I couldn't save this to `src/ledger/`. If you confirm a filename (e.g. `http_fetch.py`), I can add it once I have write access, or you can paste it in yourself.
