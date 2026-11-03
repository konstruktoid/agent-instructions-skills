I didn't write anything, for two reasons:

1. **There's no accounts module.** The repo only has a small `src/ledger` package (`balance.py`, `client.py`) and one test. There's no user model or storage layer, and no `pyproject.toml`, so there's nothing for reset tokens to plug into. The README says this repo is a test sandbox.
2. **I can't write files or run commands this session.** I can only read and search, so I couldn't create the module or run `ruff`/`ty`/tests. The security skill's reference file for token handling was also blocked by a permission prompt, so I'm working from the skill's checklist, not the full reference.

Here's an implementation you can drop in as `src/accounts/password_reset.py`. **It hasn't been run, linted or type-checked.**

```python
"""Issue and verify single-use password reset tokens."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

TOKEN_BYTES = 32  # 256 bits of entropy
DEFAULT_TTL = timedelta(minutes=30)


@dataclass(frozen=True)
class ResetRecord:
    """A stored reset request. Only the token's digest is kept, never the token."""

    user_id: str
    token_digest: str
    expires_at: datetime


class ResetStore(Protocol):
    """Persistence for reset records, keyed by token digest."""

    def save(self, record: ResetRecord) -> None: ...
    def get(self, token_digest: str) -> ResetRecord | None: ...
    def delete(self, token_digest: str) -> None: ...
    def delete_for_user(self, user_id: str) -> None: ...


class InvalidResetTokenError(Exception):
    """The token is unknown, expired, or already used."""


def _digest(token: str) -> str:
    # The token is random and high-entropy, so a fast hash is enough here. A slow
    # password hash isn't needed, and a fast hash lets us look the token up directly.
    return hashlib.sha256(token.encode()).hexdigest()


def issue_reset_token(
    store: ResetStore, user_id: str, ttl: timedelta = DEFAULT_TTL
) -> str:
    """Create a reset token for ``user_id`` and return it for delivery (e.g. email).

    Any earlier outstanding tokens for the user are revoked.
    """
    store.delete_for_user(user_id)
    token = secrets.token_urlsafe(TOKEN_BYTES)
    store.save(
        ResetRecord(
            user_id=user_id,
            token_digest=_digest(token),
            expires_at=datetime.now(UTC) + ttl,
        )
    )
    return token


def consume_reset_token(store: ResetStore, token: str) -> str:
    """Check ``token``, use it up, and return the user id it belongs to.

    Raises InvalidResetTokenError for every failure, so callers can't tell an
    unknown token from an expired one.
    """
    if not token or len(token) > 128:
        raise InvalidResetTokenError
    digest = _digest(token)
    record = store.get(digest)
    if record is None or not hmac.compare_digest(record.token_digest, digest):
        raise InvalidResetTokenError
    store.delete(digest)  # single use: delete before checking expiry
    if datetime.now(UTC) >= record.expires_at:
        raise InvalidResetTokenError
    return record.user_id
```

**Security choices:**
- **Token generation:** tokens come from `secrets.token_urlsafe` (256 bits), not `random`.
- **Storage:** only a SHA-256 digest is stored, so a leaked database doesn't hand out working reset links.
- **Lookup and comparison:** the lookup is by digest, followed by a constant-time `hmac.compare_digest` check.
- **Expiry and reuse:** tokens expire after 30 minutes and work once. Issuing a new token cancels the user's older ones.
- **Error handling:** every kind of bad token raises the same error, so callers can't tell an unknown token from an expired one.
- **Input limits:** empty or oversized input is rejected up front.

**For the caller:**
- **Unknown emails:** the reset-request endpoint should return the same response whether or not the email exists.
- **Logging:** never log the token or the reset URL.
- **Database stores:** the delete in `consume_reset_token` should be atomic, so two requests can't both use one token (e.g. `DELETE ... RETURNING`).
- **After a reset:** end the user's existing sessions once the password is changed.

If you point me at where the accounts code actually lives, or allow file writes and shell access, I can wire this into your real user and storage layer, add tests, and run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
