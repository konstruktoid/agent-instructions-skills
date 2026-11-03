I don't have a file-write tool in this session, so the code is below and wasn't saved anywhere. I also haven't run `ruff` or `ty` on it, and there's no `pyproject.toml` in the workspace to run them against. A URL sent by the client and fetched by your server is a classic way to get tricked into reaching internal addresses, so the function guards against that.

```python
"""Fetch client-supplied URLs with SSRF protections and cache the response bodies."""

from __future__ import annotations

import http.client
import ipaddress
import socket
import ssl
import threading
import time
from collections import OrderedDict
from urllib.parse import urlsplit, urlunsplit

# Only these hosts may be fetched. Set this to the hosts your feature needs.
ALLOWED_HOSTS: frozenset[str] = frozenset({"api.example.com", "cdn.example.com"})

MAX_BODY_BYTES = 5 * 1024 * 1024
TIMEOUT_SECONDS = 5.0
CACHE_TTL_SECONDS = 300.0
CACHE_MAX_ENTRIES = 256


class FetchRejectedError(ValueError):
    """Raised when a URL or its response fails a safety check."""


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection to an IP we already checked, verifying TLS against the hostname.

    Connecting to the checked IP (not resolving the name again) closes the DNS-rebinding
    gap between the check and the connection.
    """

    def __init__(self, host: str, ip: str, *, timeout: float) -> None:
        self._pinned_ip = ip
        self._tls = ssl.create_default_context()  # certificate and hostname verification on
        super().__init__(host, 443, timeout=timeout, context=self._tls)

    def connect(self) -> None:
        sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        self.sock = self._tls.wrap_socket(sock, server_hostname=self.host)


def _normalize(url: str) -> tuple[str, str, str]:
    """Check the URL and return (cache_key, host, path_and_query)."""
    parts = urlsplit(url.strip())
    if parts.scheme != "https":
        msg = "only https URLs are allowed"
        raise FetchRejectedError(msg)
    if parts.username or parts.password:
        msg = "credentials in URL are not allowed"
        raise FetchRejectedError(msg)
    if parts.port not in (None, 443):
        msg = "non-default ports are not allowed"
        raise FetchRejectedError(msg)
    host = (parts.hostname or "").rstrip(".").lower()
    if host not in ALLOWED_HOSTS:
        msg = "host is not on the allowlist"
        raise FetchRejectedError(msg)
    path = parts.path or "/"
    target = f"{path}?{parts.query}" if parts.query else path
    key = urlunsplit(("https", host, path, parts.query, ""))
    return key, host, target


def _resolve_public_ip(host: str) -> str:
    """Resolve the host and require every address to be publicly routable."""
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        msg = "host did not resolve"
        raise FetchRejectedError(msg) from exc
    addrs = {ipaddress.ip_address(info[4][0]) for info in infos}
    # Reject if any address is private, loopback, link-local (cloud metadata), or reserved.
    if not addrs or any(not a.is_global for a in addrs):
        msg = "host resolves to a non-public address"
        raise FetchRejectedError(msg)
    return str(sorted(addrs, key=str)[0])


class _TTLCache:
    """Thread-safe LRU cache whose entries expire after a fixed time."""

    def __init__(self, ttl: float, max_entries: int) -> None:
        self._ttl = ttl
        self._max = max_entries
        self._data: OrderedDict[str, tuple[float, bytes]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> bytes | None:
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return None
            expires, body = item
            if expires < time.monotonic():
                del self._data[key]
                return None
            self._data.move_to_end(key)
            return body

    def put(self, key: str, body: bytes) -> None:
        with self._lock:
            self._data[key] = (time.monotonic() + self._ttl, body)
            self._data.move_to_end(key)
            while len(self._data) > self._max:
                self._data.popitem(last=False)


_cache = _TTLCache(CACHE_TTL_SECONDS, CACHE_MAX_ENTRIES)


def fetch_cached(url: str) -> bytes:
    """Return the body of a client-supplied URL, from the cache when it's still fresh.

    Raises FetchRejectedError if the URL fails validation, resolves to a non-public
    address, redirects, returns a non-200 status, or is larger than MAX_BODY_BYTES.
    """
    key, host, target = _normalize(url)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    ip = _resolve_public_ip(host)
    conn = _PinnedHTTPSConnection(host, ip, timeout=TIMEOUT_SECONDS)
    try:
        conn.request("GET", target, headers={"Host": host, "Accept-Encoding": "identity"})
        resp = conn.getresponse()
        # http.client never follows redirects, so a 3xx can't bounce us to an internal host.
        if resp.status != 200:  # noqa: PLR2004 - only a plain 200 is cached
            msg = f"upstream returned HTTP {resp.status}"
            raise FetchRejectedError(msg)
        body = resp.read(MAX_BODY_BYTES + 1)
        if len(body) > MAX_BODY_BYTES:
            msg = "response body too large"
            raise FetchRejectedError(msg)
    finally:
        conn.close()

    _cache.put(key, body)
    return body
```

**What it protects against:**
- **Host allowlist:** only hosts you list in `ALLOWED_HOSTS` can be fetched. This is the main defense. Blocking known-bad addresses alone isn't enough, because attackers can get around it with tricks like `0x7f.1`, IPv6-mapped IPv4 addresses, or DNS names that point at internal IPs.
- **Address check:** every IP the host resolves to must be public. This blocks private ranges, loopback, link-local (including the `169.254.169.254` cloud metadata endpoint) and reserved ranges, in case an allowed name ever points somewhere internal.
- **DNS-rebinding protection:** the connection goes to the exact IP that was checked, and TLS is still verified against the real hostname.
- **No redirects:** a 3xx response is rejected, so an allowed host can't send the request on to an internal one.
- **Limits:** HTTPS only, default port only, no credentials in the URL, a 5 s timeout, a 5 MB body cap, and no compressed responses (so a small compressed reply can't expand into a huge body).
- **Cache:** keyed by the normalized URL (the `#fragment` is dropped), with a TTL and a size limit so it can't grow without bound. Only 200 responses are cached.

**Decisions for you:**
- **Allowlist contents:** if you really need to allow arbitrary public hosts, delete the `ALLOWED_HOSTS` check. The address check and IP pinning still apply, but you'd lose the strongest layer.
- **Shared cache:** the cache is per process. Use Redis or similar if you need it shared across workers.
- **Repo fit:** the workspace has no Python web framework or `pyproject.toml`, so I couldn't tell where this should go or run the lint and type checks on it. Tell me the target module and I can add it there and run `uv run ruff check`, `ruff format --check` and `ty check`.
