I couldn't create the files, so nothing has been written or tested. This session only lets me read and search files. I can't write files or run commands, so I also couldn't run the `ruff`/`ty` checks.

There's also no accounts module yet. The only Python code is `src/ledger/` (`balance.py`, `client.py`), and I found no `pyproject.toml` or lint config. Below is a proposed `src/accounts/password_reset.py`, written in the same style as the ledger code, for you to add or for me to write once I have write access.

```python
"""Issue and verify single-use password reset tokens."""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

TOKEN_BYTES = 32
TOKEN_TTL = timedelta(minutes=30)


@dataclass(frozen=True)
class ResetRecord:
    """A stored reset token, kept only as its digest."""

    user_id: str
    token_digest: str
    expires_at: datetime


class ResetStore(Protocol):
    """Persistence for reset records, keyed by token digest."""

    def save(self, record: ResetRecord) -> None: ...

    def pop(self, token_digest: str) -> ResetRecord | None:
        """Remove and return the record atomically, so a token is usable once."""
        ...

    def delete_for_user(self, user_id: str) -> None: ...


def _digest(token: str) -> str:
    # The token carries 256 bits from the CSPRNG, so a fast hash is enough;
    # a slow password hash is only needed for low-entropy secrets.
    return hashlib.sha256(token.encode()).hexdigest()


def issue_reset_token(store: ResetStore, user_id: str, now: datetime | None = None) -> str:
    """Create a reset token for a user, revoking any earlier ones.

    The raw token is returned once for delivery (e.g. an emailed link) and is never stored.
    """
    now = now or datetime.now(UTC)
    store.delete_for_user(user_id)
    token = secrets.token_urlsafe(TOKEN_BYTES)
    store.save(ResetRecord(user_id, _digest(token), now + TOKEN_TTL))
    return token


def verify_reset_token(store: ResetStore, token: str, now: datetime | None = None) -> str | None:
    """Consume a reset token and return its user id, or None if it is invalid.

    Unknown, expired and already-used tokens all fail the same way, so callers
    cannot tell them apart.
    """
    now = now or datetime.now(UTC)
    if not token or len(token) > 128:
        return None
    digest = _digest(token)
    record = store.pop(digest)
    if record is None:
        return None
    if not secrets.compare_digest(record.token_digest, digest):
        return None
    if now >= record.expires_at:
        return None
    return record.user_id
```

Design decisions:

- **Token generation:** tokens come from `secrets.token_urlsafe(32)`, never from `random`.
- **Stored as a hash:** only the SHA-256 digest is stored, so a leaked database doesn't give anyone working reset links.
- **Single use:** `pop` must remove and return the record in one atomic step (for example `DELETE … RETURNING` in SQL). Otherwise two requests racing with the same token could both succeed.
- **Expiry and revocation:** tokens last 30 minutes, and issuing a new one cancels any earlier ones for that user.
- **Same failure for every bad token:** unknown, expired and already-used tokens all return `None`. The length check stops oversized input before hashing. The `compare_digest` check is a constant-time comparison kept as a second safeguard, since the lookup by digest already does the matching.

Things the calling code should handle:

- **Same response for every email:** the "request reset" endpoint should respond the same way whether or not the email is registered, so it can't be used to discover accounts.
- **Rate limiting:** limit requests per email and per IP.
- **No logging:** never log the raw token or the reset URL.
- **After a reset:** once the password changes, end that user's existing sessions. Store the new password with bcrypt or Argon2.

If you give me write access, or tell me where the accounts code should live, I'll add this along with tests for:
- a valid token
- an expired token
- a reused token
- issuing a new token cancels the old one
- an empty or oversized token

Then I'll run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
