I couldn't save this to `src/ledger/fetch_cache.py`. The Write tool is disabled in this session, so the code is below. I also couldn't read the skill's reference files because those reads were denied. I wrote it from general SSRF guidance and didn't run `ruff` or `ty`.

```python
"""Fetch a client-supplied URL and cache the response body."""

import http.client
import ipaddress
import socket
import ssl
import threading
import time
from collections import OrderedDict
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"api.example.com"})
TIMEOUT_SECONDS = 5.0
MAX_BODY_BYTES = 1_000_000
CACHE_TTL_SECONDS = 300.0
CACHE_MAX_ENTRIES = 256

_cache: OrderedDict[str, tuple[float, bytes]] = OrderedDict()
_cache_lock = threading.Lock()


class FetchError(Exception):
    """The URL was rejected or the fetch failed."""


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection that dials a pre-validated IP, keeping TLS checks on the hostname."""

    def __init__(self, host: str, ip: str, port: int, timeout: float) -> None:
        super().__init__(host, port, timeout=timeout)
        self._ip = ip
        self._tls = ssl.create_default_context()

    def connect(self) -> None:
        sock = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._tls.wrap_socket(sock, server_hostname=self.host)


def _resolve_public_ip(host: str, port: int) -> str:
    """Resolve host and return one address, refusing any non-public result."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise FetchError("host did not resolve") from exc
    addresses = [ipaddress.ip_address(info[4][0]) for info in infos]
    if not addresses or not all(address.is_global for address in addresses):
        raise FetchError("host resolves to a non-public address")
    return str(addresses[0])


def _validate(url: str) -> tuple[str, int, str]:
    """Return (host, port, request target) for an allowed https URL."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise FetchError("only https URLs are allowed")
    if parts.username is not None or parts.password is not None:
        raise FetchError("credentials in URLs are not allowed")
    host = (parts.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise FetchError("host is not allowed")
    try:
        port = parts.port or 443
    except ValueError as exc:
        raise FetchError("invalid port") from exc
    target = parts.path or "/"
    if parts.query:
        target = f"{target}?{parts.query}"
    return host, port, target


def _download(host: str, port: int, target: str) -> bytes:
    """GET the target from a pinned public IP; redirects are not followed."""
    ip = _resolve_public_ip(host, port)
    conn = _PinnedHTTPSConnection(host, ip, port, TIMEOUT_SECONDS)
    try:
        conn.request("GET", target, headers={"Accept-Encoding": "identity"})
        response = conn.getresponse()
        if response.status != http.HTTPStatus.OK:
            raise FetchError(f"unexpected status {response.status}")
        body = response.read(MAX_BODY_BYTES + 1)
    except (OSError, http.client.HTTPException) as exc:
        raise FetchError("request failed") from exc
    finally:
        conn.close()
    if len(body) > MAX_BODY_BYTES:
        raise FetchError("response body too large")
    return body


def fetch_cached(url: str) -> bytes:
    """Return the body of an allowlisted https URL, served from a TTL/LRU cache when fresh."""
    host, port, target = _validate(url)
    key = f"{host}:{port}{target}"
    now = time.monotonic()
    with _cache_lock:
        entry = _cache.get(key)
        if entry is not None and now - entry[0] < CACHE_TTL_SECONDS:
            _cache.move_to_end(key)
            return entry[1]
    body = _download(host, port, target)
    with _cache_lock:
        _cache[key] = (now, body)
        _cache.move_to_end(key)
        while len(_cache) > CACHE_MAX_ENTRIES:
            _cache.popitem(last=False)
    return body
```

A client-supplied URL makes this a server-side request forgery (SSRF) risk, so these are the choices that matter:

- **Host allowlist:** only `https` URLs on `ALLOWED_HOSTS` are fetched. Replace the `api.example.com` placeholder with the hosts you actually need. URLs with embedded credentials are rejected.
- **Public addresses only:** every resolved address must be globally routable. This blocks loopback, private ranges, link-local ranges such as the cloud metadata IP, and similar targets.
- **DNS pinning:** the connection goes to the IP that was just validated, while TLS still verifies the certificate against the hostname. This stops DNS rebinding between the check and the connection.
- **No redirects:** a redirect response is treated as an error, so a redirect can't bounce the request to an internal host.
- **Limits:** there is a 5-second timeout and a 1 MB body cap, and only a 200 response is accepted.
- **Bounded cache:** entries expire after 5 minutes and the cache holds at most 256, evicting the least recently used. The key is built from the validated host, port and target, so a client can't fill the cache with unlimited variants of the same URL.
- **Cached bytes:** the body is stored as raw bytes, never decoded or deserialized. Decode it only at the point of use.

Once the file is in place, run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`. If you grant read access to the skill's `references/` directory, I can also check the code against it.
