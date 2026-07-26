I don't have file-write access in this session (only read/search tools are enabled), so I can't create the files directly. Here's the implementation to add to `src/accounts/reset_tokens.py`, following the same conventions as `src/ledger/`:

```python
"""Issue and verify single-use password reset tokens."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

TOKEN_TTL = timedelta(minutes=30)


@dataclass
class ResetTokenRecord:
    """A stored password reset token, keyed by the hash of the raw token."""

    user_id: str
    token_hash: str
    expires_at: datetime


class ResetTokenStore:
    """Backing store for reset token records, keyed by token hash.

    Only the hash of each token is ever stored, so a leak of the store does
    not by itself let an attacker reset a password.
    """

    def __init__(self) -> None:
        self._by_hash: dict[str, ResetTokenRecord] = {}

    def save(self, record: ResetTokenRecord) -> None:
        self._by_hash[record.token_hash] = record

    def get(self, token_hash: str) -> ResetTokenRecord | None:
        return self._by_hash.get(token_hash)

    def delete(self, token_hash: str) -> None:
        self._by_hash.pop(token_hash, None)

    def delete_for_user(self, user_id: str) -> None:
        stale = [h for h, r in self._by_hash.items() if r.user_id == user_id]
        for token_hash in stale:
            del self._by_hash[token_hash]


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_reset_token(user_id: str, store: ResetTokenStore) -> str:
    """Issue a reset token for user_id and return the raw token to send to them.

    Any previously issued, unused token for this user is invalidated so only
    one reset link is ever live at a time.
    """
    store.delete_for_user(user_id)
    token = secrets.token_urlsafe(32)
    store.save(
        ResetTokenRecord(
            user_id=user_id,
            token_hash=_hash_token(token),
            expires_at=datetime.now(UTC) + TOKEN_TTL,
        )
    )
    return token


def verify_reset_token(token: str, store: ResetTokenStore) -> str | None:
    """Verify a reset token and consume it, returning the user_id, or None if
    the token is unknown, already used, or expired.
    """
    record = store.get(_hash_token(token))
    if record is None:
        return None
    store.delete(record.token_hash)
    if datetime.now(UTC) > record.expires_at:
        return None
    return record.user_id
```

Security choices, per the python-secure-coding skill:
- **Token generation**: `secrets.token_urlsafe(32)` (CSPRNG, 256 bits), never `random`.
- **Storage**: only the SHA-256 hash of the token is persisted — a store/DB leak alone can't be used to reset a password.
- **Single-use**: `verify_reset_token` deletes the record before checking expiry, so a token can't be replayed even if verification fails partway.
- **Expiry**: 30-minute TTL, checked with timezone-aware UTC timestamps.
- **One live token per user**: issuing a new token invalidates any prior unused one, shrinking the attack window.
- Lookup is by hash via dict `get`, not a manual byte-by-byte compare of the raw token, so there's no meaningful timing side channel to guard with `hmac.compare_digest`.

Not included, since it's the caller's responsibility outside this module: the reset-request endpoint should return the same response whether or not the email exists (avoid account enumeration), and should rate-limit reset requests.

I couldn't run `ruff`/`ty` or add tests since I have no write/execute tools this session — if you'd like, re-run with those tools enabled and I'll create the files, add tests mirroring `tests/test_balance.py`, and verify the lint/type-check loop.
