I wrote this as a single module using only the Python standard library. Your project's `src/ledger/` has no HTTP client yet, so it adds no dependencies. I couldn't save it to the repository or run `ruff`/`ty` on it, because I only had read-only tools in this session.

```python
"""Fetch client-supplied URLs with SSRF protections and cache the response bodies."""

import http.client
import ipaddress
import socket
import ssl
import threading
from collections import OrderedDict
from urllib.parse import urlsplit

# Only these destinations may be fetched; everything else is rejected (fail closed).
ALLOWED_HOSTS = frozenset({"api.example.com"})
ALLOWED_PORTS = frozenset({443})
MAX_URL_LENGTH = 2048
MAX_BODY_BYTES = 1_000_000
TIMEOUT_SECONDS = 5.0
CACHE_MAX_ENTRIES = 256

_cache: OrderedDict[str, bytes] = OrderedDict()
_cache_lock = threading.Lock()


class UnsafeURLError(ValueError):
    """Raised when a client-supplied URL fails destination validation."""


class FetchError(RuntimeError):
    """Raised when an allowed URL could not be fetched successfully."""


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection to a pre-validated IP, verifying TLS against the hostname."""

    def __init__(self, host: str, ip: str, port: int, timeout: float) -> None:
        self._tls_context = ssl.create_default_context()
        super().__init__(host, port, timeout=timeout, context=self._tls_context)
        self._pinned_ip = ip

    def connect(self) -> None:
        # Connect to the IP we already checked, so a second DNS lookup cannot
        # rebind the hostname to an internal address.
        sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        self.sock = self._tls_context.wrap_socket(sock, server_hostname=self.host)


def _validate_url(url: str) -> tuple[str, int, str]:
    """Return (host, port, request target) for an allowlisted HTTPS URL."""
    if len(url) > MAX_URL_LENGTH:
        msg = "URL too long"
        raise UnsafeURLError(msg)
    parts = urlsplit(url)
    if parts.scheme != "https":
        msg = "only https URLs are allowed"
        raise UnsafeURLError(msg)
    if parts.username is not None or parts.password is not None:
        msg = "credentials in URL are not allowed"
        raise UnsafeURLError(msg)
    host = (parts.hostname or "").rstrip(".")
    if host not in ALLOWED_HOSTS:
        msg = "host is not allowed"
        raise UnsafeURLError(msg)
    try:
        port = parts.port or 443
    except ValueError as exc:
        msg = "invalid port"
        raise UnsafeURLError(msg) from exc
    if port not in ALLOWED_PORTS:
        msg = "port is not allowed"
        raise UnsafeURLError(msg)
    target = parts.path or "/"
    if parts.query:
        target = f"{target}?{parts.query}"
    return host, port, target


def _resolve_public_ip(host: str, port: int) -> str:
    """Resolve host and return an address, rejecting it if any record is non-public."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        msg = "host did not resolve"
        raise FetchError(msg) from exc
    addresses = sorted({str(info[4][0]) for info in infos})
    if not addresses:
        msg = "host did not resolve"
        raise FetchError(msg)
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        if not ip.is_global:
            msg = "host resolves to a non-public address"
            raise UnsafeURLError(msg)
    return addresses[0]


def fetch_cached(url: str) -> bytes:
    """Fetch an allowlisted HTTPS URL supplied by a client and cache its body.

    Raises UnsafeURLError if the destination is not permitted, and FetchError if
    the request fails, redirects, returns a non-200 status, or exceeds MAX_BODY_BYTES.
    """
    host, port, target = _validate_url(url)
    cache_key = f"https://{host}:{port}{target}"
    with _cache_lock:
        if cache_key in _cache:
            _cache.move_to_end(cache_key)
            return _cache[cache_key]

    ip = _resolve_public_ip(host, port)
    conn = _PinnedHTTPSConnection(host, ip, port, TIMEOUT_SECONDS)
    try:
        conn.request("GET", target, headers={"Accept-Encoding": "identity"})
        response = conn.getresponse()
        # http.client never follows redirects; refusing 3xx keeps the allowlist authoritative.
        if response.status != http.client.OK:
            msg = f"upstream returned status {response.status}"
            raise FetchError(msg)
        body = response.read(MAX_BODY_BYTES + 1)
    except (OSError, http.client.HTTPException) as exc:
        msg = "upstream request failed"
        raise FetchError(msg) from exc
    finally:
        conn.close()
    if len(body) > MAX_BODY_BYTES:
        msg = "response body too large"
        raise FetchError(msg)

    with _cache_lock:
        _cache[cache_key] = body
        _cache.move_to_end(cache_key)
        while len(_cache) > CACHE_MAX_ENTRIES:
            _cache.popitem(last=False)
    return body
```

## How it guards against SSRF

Because the URL comes from the client, the main risk is someone using the server to reach internal addresses. It guards against that in five ways:

- **Exact host allowlist.** Only `https` URLs to hosts in `ALLOWED_HOSTS` on allowed ports are fetched, and URLs with embedded credentials are rejected. Anything that isn't explicitly allowed is refused. Change `api.example.com` to your real upstream(s).
- **Every DNS answer is checked.** If any address the host resolves to isn't a public internet address, the request is refused. That covers loopback, private ranges, link-local, cloud metadata addresses like `169.254.169.254`, and IPv4 addresses disguised as IPv6.
- **The checked IP is the one used.** The connection goes to the exact IP that passed the check, so the hostname can't be quietly switched to an internal address between the check and the request. TLS still verifies the certificate against the real hostname.
- **No redirects.** A redirect would send the request somewhere the allowlist never approved, so any 3xx response is treated as an error.
- **Size and time limits.** There's a 5-second timeout, a 1 MB body cap, and a limited URL length.

## How the cache works

- Entries are keyed by the cleaned-up URL (fragment dropped, default port filled in), so equivalent URLs share one entry.
- It holds up to 256 entries and drops the least recently used first.
- It's safe to use from multiple threads.
- Only successful responses are stored.
- Nothing expires on a timer. If you need freshness, add a timestamp to each entry.

## Next steps

- Save the code as, for example, `src/ledger/fetch.py`.
- Run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`. I haven't run them, so it isn't verified yet.
- Add tests for the rejection cases: an `http` URL, a host not on the allowlist, a host that resolves to `127.0.0.1`, and an oversized body.
