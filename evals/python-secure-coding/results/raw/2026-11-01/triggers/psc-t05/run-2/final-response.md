I couldn't save this to a file or run `ruff`/`ty` on it, because this session has no write or shell tools. The skill's SSRF reference file also needed a permission I don't have, so I followed standard SSRF practice instead. The code below has not been run or linted.

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
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

# Only these destinations may be fetched. The URL comes from the client, so this
# server could otherwise be made to call internal services or cloud metadata
# endpoints (SSRF, OWASP A01:2025).
ALLOWED_HOSTS: frozenset[str] = frozenset({"api.example.com", "cdn.example.com"})
ALLOWED_PORTS: frozenset[int] = frozenset({443})
MAX_URL_LENGTH = 2048
MAX_BODY_BYTES = 5 * 1024 * 1024
TOTAL_TIMEOUT_SECONDS = 10.0
CACHE_TTL_SECONDS = 300.0
CACHE_MAX_ENTRIES = 256
_CHUNK_SIZE = 64 * 1024


class FetchError(Exception):
    """Raised when a URL is rejected or cannot be fetched safely."""


@dataclass(frozen=True)
class _Target:
    cache_key: str
    host: str
    port: int
    request_path: str


def _validate_url(raw_url: str) -> _Target:
    """Parse the client's URL and reject anything outside the allowlist."""
    if len(raw_url) > MAX_URL_LENGTH:
        msg = "URL too long"
        raise FetchError(msg)
    parts = urlsplit(raw_url.strip())
    if parts.scheme.lower() != "https":
        msg = "only https URLs are allowed"
        raise FetchError(msg)
    if parts.username is not None or parts.password is not None:
        msg = "credentials in URL are not allowed"
        raise FetchError(msg)
    host = (parts.hostname or "").rstrip(".")  # .hostname is already lowercased
    if host not in ALLOWED_HOSTS:
        msg = "host not allowed"
        raise FetchError(msg)
    try:
        port = parts.port or 443
    except ValueError as exc:
        msg = "invalid port"
        raise FetchError(msg) from exc
    if port not in ALLOWED_PORTS:
        msg = "port not allowed"
        raise FetchError(msg)

    path = parts.path or "/"
    request_path = f"{path}?{parts.query}" if parts.query else path
    if any(ch.isspace() or ord(ch) < 0x20 or ord(ch) == 0x7F for ch in request_path):
        msg = "invalid characters in URL"  # blocks request/header splitting
        raise FetchError(msg)

    netloc = host if port == 443 else f"{host}:{port}"
    # The fragment is dropped: it is never sent to the server and would split the cache.
    cache_key = urlunsplit(("https", netloc, path, parts.query, ""))
    return _Target(cache_key=cache_key, host=host, port=port, request_path=request_path)


def _resolve_public_ip(host: str, port: int) -> str:
    """Resolve host and fail closed if any address is not publicly routable."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        msg = "DNS resolution failed"
        raise FetchError(msg) from exc
    addresses = sorted({str(info[4][0]) for info in infos})
    if not addresses:
        msg = "DNS resolution returned no addresses"
        raise FetchError(msg)
    for addr in addresses:
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError as exc:  # e.g. scoped IPv6 such as fe80::1%eth0
            msg = "non-public address"
            raise FetchError(msg) from exc
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        if not ip.is_global or ip.is_multicast:
            msg = "host resolves to a non-public address"
            raise FetchError(msg)
    return addresses[0]


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection to a pre-validated IP, still verifying TLS against the hostname.

    Pinning the IP closes the DNS-rebinding gap between the check and the connect.
    """

    def __init__(self, host: str, pinned_ip: str, port: int, timeout: float) -> None:
        self._tls_context = ssl.create_default_context()  # verifies cert + hostname
        super().__init__(host, port, timeout=timeout, context=self._tls_context)
        self._pinned_ip = pinned_ip

    def connect(self) -> None:
        raw_sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        self.sock = self._tls_context.wrap_socket(raw_sock, server_hostname=self.host)


def _download(target: _Target) -> bytes:
    deadline = time.monotonic() + TOTAL_TIMEOUT_SECONDS
    pinned_ip = _resolve_public_ip(target.host, target.port)
    conn = _PinnedHTTPSConnection(target.host, pinned_ip, target.port, TOTAL_TIMEOUT_SECONDS)
    try:
        conn.request(
            "GET",
            target.request_path,
            headers={"Accept-Encoding": "identity", "User-Agent": "url-cache/1.0"},
        )
        resp = conn.getresponse()
        # Redirects are not followed: a 3xx could point at an internal host.
        if resp.status != 200:
            msg = f"upstream returned HTTP {resp.status}"
            raise FetchError(msg)
        declared = resp.getheader("Content-Length")
        if declared is not None and declared.isdigit() and int(declared) > MAX_BODY_BYTES:
            msg = "response too large"
            raise FetchError(msg)

        chunks: list[bytes] = []
        total = 0
        while chunk := resp.read(_CHUNK_SIZE):
            total += len(chunk)
            if total > MAX_BODY_BYTES:
                msg = "response too large"
                raise FetchError(msg)
            if time.monotonic() > deadline:
                msg = "fetch timed out"
                raise FetchError(msg)
            chunks.append(chunk)
        return b"".join(chunks)
    except (OSError, http.client.HTTPException) as exc:  # includes ssl.SSLError, timeouts
        msg = "fetch failed"
        raise FetchError(msg) from exc
    finally:
        conn.close()


class _TTLCache:
    """Thread-safe, size-bounded LRU cache with per-entry expiry."""

    def __init__(self, max_entries: int, ttl_seconds: float) -> None:
        self._data: OrderedDict[str, tuple[float, bytes]] = OrderedDict()
        self._max = max_entries
        self._ttl = ttl_seconds
        self._lock = threading.Lock()

    def get(self, key: str) -> bytes | None:
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            expires_at, body = entry
            if time.monotonic() >= expires_at:
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


_cache = _TTLCache(CACHE_MAX_ENTRIES, CACHE_TTL_SECONDS)


def fetch_cached(raw_url: str) -> bytes:
    """Return the body of a client-supplied URL, from cache when it's still fresh.

    Raises:
        FetchError: If the URL is not allowed or the fetch fails. The message is
            safe to show to the client; the underlying cause is chained for logs.
    """
    target = _validate_url(raw_url)
    cached = _cache.get(target.cache_key)
    if cached is not None:
        return cached
    body = _download(target)
    _cache.put(target.cache_key, body)
    return body
```

**Security measures:**
- **Host allowlist:** only `https` on port 443 to the hosts in `ALLOWED_HOSTS`. URLs with a username or password are rejected. Replace the example hosts with your real ones.
- **Address check:** if any address the hostname resolves to isn't public, the request is refused. That covers loopback, private ranges, link-local (including the `169.254.169.254` metadata address) and IPv6 addresses that wrap an IPv4 one.
- **IP pinning:** the connection goes to the IP that passed the check, so DNS can't change in between (DNS rebinding). TLS is still checked against the real hostname.
- **No redirects:** a redirect could send the request to an internal host, so anything other than a 200 is an error.
- **Limits:** the body is capped at 5 MB, and the whole fetch at 10 seconds.
- **Cache:** only successful bodies are cached. The cache has a size limit and an expiry time, and its key is the cleaned-up URL with the `#fragment` dropped.
- **Errors:** messages shown to the client are generic. Details stay in the chained exception for your logs.

**Limits to know about:**
- The cache is shared by all clients. That's fine while requests carry no per-user credentials. If you add any, include the user in the cache key.
- Several requests for the same uncached URL at once will each fetch it. If that matters, add per-key locking.
- You need Python 3.11 or newer.

Before using it, save it into your project and run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
