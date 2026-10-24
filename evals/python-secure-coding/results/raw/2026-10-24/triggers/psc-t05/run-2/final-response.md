I couldn't save this as a file or run anything. This session has no tool for writing files or running commands, so I'm giving you the module to paste in, probably as `src/ledger/fetch.py`. I haven't run it or checked it with `ruff` or `ty`.

Letting a client choose which URL your server fetches is risky. It's called server-side request forgery (SSRF): someone could make your server request its own internal services, cloud metadata endpoints or private addresses. So the function only fetches from hosts on a list you set, and blocks the usual workarounds.

```python
"""Fetch client-supplied URLs with SSRF protections and cache the response bodies."""

import http.client
import ipaddress
import socket
import ssl
import threading
import time
from collections import OrderedDict
from urllib.parse import urlsplit

# Only these hosts may be fetched. Client input never widens this set.
ALLOWED_HOSTS = frozenset({"api.example.com"})
MAX_BODY_BYTES = 1_000_000
TIMEOUT_SECONDS = 5.0
CACHE_TTL_SECONDS = 300.0
CACHE_MAX_ENTRIES = 256

_cache: OrderedDict[str, tuple[float, bytes]] = OrderedDict()
_cache_lock = threading.Lock()


class FetchError(Exception):
    """Raised when a URL is rejected or cannot be fetched safely."""


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection to a pre-validated IP, verifying the certificate against the hostname."""

    def __init__(
        self, host: str, ip: str, port: int, context: ssl.SSLContext, timeout: float
    ) -> None:
        super().__init__(host, port, timeout=timeout, context=context)
        self._pinned_ip = ip
        self._tls_context = context

    def connect(self) -> None:
        # Connect to the IP we validated, not a fresh DNS lookup (blocks DNS rebinding).
        sock = socket.create_connection((self._pinned_ip, self.port), self.timeout)
        self.sock = self._tls_context.wrap_socket(sock, server_hostname=self.host)


def _validate_url(url: str) -> tuple[str, int, str]:
    """Return (host, port, request target) for an allowlisted HTTPS URL, or raise FetchError."""
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise FetchError("only https URLs are allowed")
    if parts.username or parts.password:
        raise FetchError("credentials in URL are not allowed")
    host = (parts.hostname or "").lower().rstrip(".")
    if host not in ALLOWED_HOSTS:
        raise FetchError("host is not allowed")
    try:
        port = parts.port or 443
    except ValueError as exc:
        raise FetchError("invalid port") from exc
    if port != 443:
        raise FetchError("port is not allowed")
    target = parts.path or "/"
    if parts.query:
        target = f"{target}?{parts.query}"
    return host, port, target


def _resolve_public_ip(host: str, port: int) -> str:
    """Resolve host and return one address, failing closed if any address is non-public."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise FetchError("could not resolve host") from exc
    addresses = {str(info[4][0]) for info in infos}
    if not addresses:
        raise FetchError("could not resolve host")
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:  # e.g. scoped link-local "fe80::1%eth0"
            raise FetchError("host resolves to a disallowed address") from exc
        mapped = getattr(ip, "ipv4_mapped", None)
        if not ip.is_global or (mapped is not None and not mapped.is_global):
            raise FetchError("host resolves to a disallowed address")
    return sorted(addresses)[0]


def _fetch(host: str, port: int, target: str) -> bytes:
    """GET the target from the pinned host; redirects are not followed."""
    ip = _resolve_public_ip(host, port)
    conn = _PinnedHTTPSConnection(
        host, ip, port, ssl.create_default_context(), TIMEOUT_SECONDS
    )
    try:
        conn.request("GET", target, headers={"Accept-Encoding": "identity"})
        response = conn.getresponse()
        if response.status != 200:
            raise FetchError(f"upstream returned HTTP {response.status}")
        body = response.read(MAX_BODY_BYTES + 1)
    except (OSError, http.client.HTTPException) as exc:
        raise FetchError("fetch failed") from exc
    finally:
        conn.close()
    if len(body) > MAX_BODY_BYTES:
        raise FetchError("response body too large")
    return body


def fetch_cached(url: str) -> bytes:
    """Fetch a client-supplied URL and return its body, caching successful responses."""
    host, port, target = _validate_url(url)
    key = f"https://{host}{target}"
    now = time.monotonic()
    with _cache_lock:
        entry = _cache.get(key)
        if entry is not None and entry[0] > now:
            _cache.move_to_end(key)
            return entry[1]

    body = _fetch(host, port, target)

    with _cache_lock:
        _cache[key] = (now + CACHE_TTL_SECONDS, body)
        _cache.move_to_end(key)
        while len(_cache) > CACHE_MAX_ENTRIES:
            _cache.popitem(last=False)
    return body
```

**What it guards against:**
- **Approved hosts only:** the URL must be `https`, on port 443, with no username or password in it, and its host must be in `ALLOWED_HOSTS`. Set that to your real upstream hosts; there is no option to let client input add hosts.
- **Hosts that point inward:** it looks up every address the host resolves to and refuses the request if any of them is private, loopback, link-local (including the `169.254.169.254` metadata address) or otherwise not a public address. This includes IPv4 addresses written in IPv6 form.
- **DNS rebinding:** a host could resolve to a public address when checked and an internal one a moment later. To prevent that, the connection goes to the exact address that was checked, while the TLS certificate is still verified against the hostname.
- **Redirects:** they aren't followed, so an approved host can't bounce the request somewhere internal. Any response other than 200 raises `FetchError`.
- **Resource limits:** bodies are capped at 1 MB and each network step has a 5-second timeout. The cache holds 256 entries for 5 minutes each, dropping the least recently used first, and is safe to use from multiple threads.
- **Error messages:** `FetchError` messages are generic, so a client can't use them to probe your internal network.

**Limitations:**
- The timeout applies to each network step, not the whole request, so a server that sends data very slowly can hold a worker for longer than 5 seconds. If that matters, run the fetch under an overall deadline.
- All clients share one cache. That's only safe while requests carry no credentials or cookies. If you ever add an auth header, include the user in the cache key.
- At the same moment, two requests for the same uncached URL will both fetch it.
- `connect` handles HTTPS only. If you later allow a proxy, this approach no longer works.

**Not done:**
- I was refused permission to read the skill's SSRF reference file, so this is based on standard SSRF guidance rather than that document.
- The workspace has no `pyproject.toml`, and I couldn't run `uv run ruff check .`, `uv run ruff format --check .` or `uv run ty check` here. Please run them, plus a quick test against a real allowed host, before relying on this.
