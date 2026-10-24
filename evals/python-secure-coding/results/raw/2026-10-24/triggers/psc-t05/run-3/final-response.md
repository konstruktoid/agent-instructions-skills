I couldn't save this as a file or run the checks, because this session has no file-writing or shell tools. So `ruff check`, `ruff format --check` and `ty check` have **not** been run against this code. The project has no HTTP library, so it uses only the standard library. Suggested location: `src/ledger/fetch.py`.

```python
"""Fetch client-supplied URLs with SSRF protections and cache the response bodies."""

import http.client
import ipaddress
import socket
import ssl
import threading
from collections import OrderedDict
from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"api.example.com"})
HTTPS_PORT = 443
TIMEOUT_SECONDS = 5.0
MAX_BODY_BYTES = 1_000_000
MAX_CACHE_ENTRIES = 256

_cache: OrderedDict[str, bytes] = OrderedDict()
_cache_lock = threading.Lock()


class FetchError(Exception):
    """Raised when a URL is rejected or its response cannot be used."""


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection to a pre-validated IP that still verifies the certificate for the host."""

    def __init__(self, host: str, ip: str) -> None:
        super().__init__(host, HTTPS_PORT, timeout=TIMEOUT_SECONDS)
        self._pinned_ip = ip
        self._tls = ssl.create_default_context()

    def connect(self) -> None:
        sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        self.sock = self._tls.wrap_socket(sock, server_hostname=self.host)


def _validate_url(url: str) -> tuple[str, str]:
    """Return (host, request_target) for an allowlisted HTTPS URL, or raise FetchError."""
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise FetchError("malformed URL") from exc
    host = parts.hostname
    if parts.scheme != "https" or host is None or host not in ALLOWED_HOSTS:
        raise FetchError("URL not allowed")
    if parts.username is not None or parts.password is not None:
        raise FetchError("credentials in URL not allowed")
    if port not in (None, HTTPS_PORT):
        raise FetchError("port not allowed")
    target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    return host, target


def _resolve_public_ip(host: str) -> str:
    """Resolve host and return one address, failing closed if any address is non-public."""
    try:
        infos = socket.getaddrinfo(host, HTTPS_PORT, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise FetchError("host did not resolve") from exc
    addresses = []
    for info in infos:
        ip = ipaddress.ip_address(str(info[4][0]).split("%", 1)[0])
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped
        if not ip.is_global:
            raise FetchError("host resolves to a non-public address")
        addresses.append(str(ip))
    if not addresses:
        raise FetchError("host did not resolve")
    return addresses[0]


def fetch_cached(url: str) -> bytes:
    """Fetch an allowlisted HTTPS URL supplied by a client, caching successful bodies.

    The URL is untrusted: only allowlisted hosts over HTTPS are fetched, the connection
    is pinned to the address that was validated (defeating DNS rebinding), redirects are
    not followed, and the body size and request time are bounded.
    """
    host, target = _validate_url(url)
    key = f"https://{host}{target}"
    with _cache_lock:
        if key in _cache:
            _cache.move_to_end(key)
            return _cache[key]

    conn = _PinnedHTTPSConnection(host, _resolve_public_ip(host))
    try:
        conn.request("GET", target, headers={"Host": host})
        response = conn.getresponse()
        if response.status != http.client.OK:
            raise FetchError(f"upstream returned status {response.status}")
        body = response.read(MAX_BODY_BYTES + 1)
    except (OSError, http.client.HTTPException) as exc:
        raise FetchError("upstream request failed") from exc
    finally:
        conn.close()
    if len(body) > MAX_BODY_BYTES:
        raise FetchError("response body too large")

    with _cache_lock:
        _cache[key] = body
        _cache.move_to_end(key)
        while len(_cache) > MAX_CACHE_ENTRIES:
            _cache.popitem(last=False)
    return body
```

**How it guards against server-side request forgery (SSRF):**
- **Host allowlist:** only hosts in `ALLOWED_HOSTS`, over HTTPS on port 443, with no username or password in the URL. `api.example.com` is a placeholder; put your real upstream hosts there. If clients really must reach any host, the address check below becomes the only protection, so tell me and we can tighten it.
- **Address check:** the host is looked up and the request is refused if **any** of its addresses is non-public. This covers loopback, private ranges, the link-local cloud metadata address `169.254.169.254`, and IPv4 addresses hidden inside IPv6 ones.
- **Pinned connection:** it connects to the exact address that passed the check, so a DNS answer that changes between the check and the request can't redirect it. TLS still verifies the certificate against the real hostname.
- **No redirects:** `http.client` doesn't follow them, and anything other than a 200 response is rejected. A redirect can't send the request to an internal address.
- **Limits:** a 5-second timeout and a 1 MB body cap keep a slow or huge response from tying up the server or filling memory.

**Cache:** the key is the rebuilt URL, so the fragment and any explicit `:443` are ignored. It holds at most 256 entries, drops the least recently used first, and is thread-safe. Failed fetches are never cached. It has no expiry; add a timestamp per entry if bodies can go stale.

**Notes:**
- The fetcher sends no credentials or cookies. Don't add your service's auth headers to these requests.
- `FetchError` messages are generic, so they're safe to pass back to the client. Log the chained cause on the server instead.

To check it once it's saved, run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`. The most likely complaint is the `connect` override's types. A test that mocks `socket.getaddrinfo` to return `127.0.0.1` and checks that a `FetchError` is raised would cover the address check.
