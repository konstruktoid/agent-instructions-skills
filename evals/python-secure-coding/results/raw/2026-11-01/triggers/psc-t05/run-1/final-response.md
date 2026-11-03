I couldn't create the file or run any checks. This session has no file-writing or shell tool, so the code is below for you to save, for example as `src/ledger/fetch_cache.py`. Three things to know first:

- **Nothing was run:** `ruff` and `ty` haven't been run on this code, and nothing has tested it.
- **No `uv` project:** the repo has no `pyproject.toml`, so there's no `uv` setup to run checks through.
- **Reference not applied:** I wasn't given permission to read the skill's server-side request guidance (`references/access-control.md`). The protections below come from general practice, not from that file.

Fetching a URL that a client supplies is a server-side request forgery (SSRF) risk: a client can make your server call internal addresses it can reach and they can't. The function is built around stopping that.

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
from urllib.parse import urlsplit

# Only these hosts may be fetched. Matching is exact; there are no wildcards or suffix matches.
ALLOWED_HOSTS: frozenset[str] = frozenset({"api.example.com"})
ALLOWED_PORT = 443
TIMEOUT_SECONDS = 5.0
MAX_BODY_BYTES = 1_000_000
CACHE_TTL_SECONDS = 300.0
CACHE_MAX_ENTRIES = 256


class FetchRejectedError(ValueError):
    """The URL or its resolved address is not permitted."""


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection to a pre-validated IP, verifying TLS against the original hostname."""

    def __init__(self, host: str, ip: str, *, timeout: float) -> None:
        super().__init__(host, ALLOWED_PORT, timeout=timeout, context=ssl.create_default_context())
        self._pinned_ip = ip

    def connect(self) -> None:
        raw = socket.create_connection((self._pinned_ip, self.port), timeout=self.timeout)
        self.sock = self._context.wrap_socket(raw, server_hostname=self.host)  # type: ignore[attr-defined]  # private stdlib attr; holds the context passed above


class _TTLCache:
    """Bounded, thread-safe LRU cache whose entries expire after a fixed time."""

    def __init__(self, max_entries: int, ttl: float) -> None:
        self._data: OrderedDict[str, tuple[float, bytes]] = OrderedDict()
        self._max = max_entries
        self._ttl = ttl
        self._lock = threading.Lock()

    def get(self, key: str) -> bytes | None:
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            expires, body = entry
            if time.monotonic() >= expires:
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


def _validate_url(url: str) -> tuple[str, str]:
    """Return (hostname, path_with_query) or raise FetchRejectedError."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise FetchRejectedError("only https URLs are allowed")
    if parts.username or parts.password:
        raise FetchRejectedError("credentials in URL are not allowed")
    host = (parts.hostname or "").lower().rstrip(".")
    if host not in ALLOWED_HOSTS:
        raise FetchRejectedError("host is not allowed")
    if parts.port not in (None, ALLOWED_PORT):
        raise FetchRejectedError("port is not allowed")
    path = parts.path or "/"
    if parts.query:
        path = f"{path}?{parts.query}"
    return host, path


def _resolve_public_ip(host: str) -> str:
    """Resolve host and return one address, refusing if any resolved address is non-public."""
    try:
        infos = socket.getaddrinfo(host, ALLOWED_PORT, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise FetchRejectedError("host did not resolve") from exc
    addresses = {info[4][0] for info in infos}
    if not addresses:
        raise FetchRejectedError("host did not resolve")
    for addr in addresses:
        if not ipaddress.ip_address(addr).is_global:
            raise FetchRejectedError("host resolves to a non-public address")
    return sorted(addresses)[0]


def fetch_cached(url: str) -> bytes:
    """Fetch an allowlisted HTTPS URL and return its body, serving from cache when fresh.

    Raises FetchRejectedError for disallowed URLs, and OSError/http.client.HTTPException
    for transport failures. Redirects are not followed; non-200 responses raise.
    """
    host, path = _validate_url(url)
    cache_key = f"https://{host}{path}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    ip = _resolve_public_ip(host)
    conn = _PinnedHTTPSConnection(host, ip, timeout=TIMEOUT_SECONDS)
    try:
        conn.request("GET", path, headers={"Host": host, "Accept-Encoding": "identity"})
        resp = conn.getresponse()
        if resp.status != http.client.OK:
            raise FetchRejectedError(f"upstream returned status {resp.status}")
        body = resp.read(MAX_BODY_BYTES + 1)
        if len(body) > MAX_BODY_BYTES:
            raise FetchRejectedError("response body too large")
    finally:
        conn.close()

    _cache.put(cache_key, body)
    return body
```

## How it limits SSRF

- **Allowlists:** only `https`, only the exact hosts in `ALLOWED_HOSTS`, and only port 443 are accepted. URLs with a username or password are refused. Replace `api.example.com` with your real hosts.
- **Address checks:** the hostname is looked up once, and the fetch is refused if any resulting address isn't public. That blocks loopback, private ranges, link-local addresses (including the cloud metadata address `169.254.169.254`) and IPv6 equivalents.
- **No DNS rebinding:** the connection goes to the address that was checked, while the certificate is still verified against the original hostname. A second lookup can't swap in an internal address.
- **No redirects:** `http.client` doesn't follow them, so a redirect can't send the request to an internal address.
- **Limits:** a 5-second timeout and a 1 MB body cap stop slow or huge responses. Only 200 responses are cached.
- **Cache:** entries are keyed on the cleaned-up URL. The cache is size-limited, entries expire after 5 minutes, and it's safe to use from multiple threads, so clients can't make it grow without limit.

## Things to check

- **Pinned connection:** `_PinnedHTTPSConnection` relies on `self._context`, a private attribute of Python's own `http.client`. I added a narrow type-ignore with a reason for it; `ty` may want its own suppression syntax instead.
- **Shared cache:** the cache is shared across all clients. If responses vary by caller (auth headers, cookies), add the caller's identity to the cache key, or don't cache those responses.

To verify, once the project has a `pyproject.toml`, run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
