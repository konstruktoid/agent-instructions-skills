I couldn't write this into the repo, for two reasons:

1. **There's no accounts module.** The only Python code is `src/ledger/` (`balance.py`, `client.py`) and `tests/test_balance.py`. I don't know where your user records or storage live.
2. **I can't edit files or run commands in this session.** I can only read and search, so I couldn't create files or run `uv run ruff check`, `ruff format --check` or `ty check`. Treat the code below as **untested and not linted**. I also couldn't open the skill's `references/secrets.md` (the read was blocked), so this follows standard practice rather than that file.

Here is a proposed `src/accounts/reset_tokens.py`. It stores tokens through an interface you'd connect to your real database:

```python
"""Issue and verify single-use password reset tokens."""

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

RESET_TOKEN_TTL = timedelta(minutes=30)
_TOKEN_BYTES = 32


@dataclass(frozen=True)
class ResetTokenRecord:
    """A stored reset token, keyed by its hash; the raw token is never persisted."""

    user_id: str
    token_hash: str
    expires_at: datetime
    used: bool = False


class ResetTokenStore(Protocol):
    """Persistence for reset tokens."""

    def save(self, record: ResetTokenRecord) -> None: ...
    def get_by_hash(self, token_hash: str) -> ResetTokenRecord | None: ...
    def mark_used(self, token_hash: str) -> bool:
        """Atomically mark unused token as used; return False if already used."""
        ...
    def revoke_for_user(self, user_id: str) -> None: ...


def _hash_token(token: str) -> str:
    # The token is 256 bits of CSPRNG output, so a fast hash is sufficient here;
    # slow password hashing (Argon2/bcrypt) is for low-entropy human secrets.
    return hashlib.sha256(token.encode()).hexdigest()


def issue_reset_token(store: ResetTokenStore, user_id: str, now: datetime | None = None) -> str:
    """Create a reset token for a user and return the raw token to deliver out of band."""
    now = now or datetime.now(UTC)
    store.revoke_for_user(user_id)  # only one live token per user
    token = secrets.token_urlsafe(_TOKEN_BYTES)
    store.save(
        ResetTokenRecord(
            user_id=user_id,
            token_hash=_hash_token(token),
            expires_at=now + RESET_TOKEN_TTL,
        )
    )
    return token


def verify_reset_token(store: ResetTokenStore, token: str, now: datetime | None = None) -> str | None:
    """Consume a reset token and return its user id, or None if invalid, expired, or used."""
    if not token or len(token) > 128:  # reject junk at the boundary
        return None
    now = now or datetime.now(UTC)
    token_hash = _hash_token(token)
    record = store.get_by_hash(token_hash)
    if record is None or record.used or record.expires_at <= now:
        return None
    # Defense in depth: lookup is by hash, but compare in constant time anyway.
    if not secrets.compare_digest(record.token_hash, token_hash):
        return None
    if not store.mark_used(token_hash):  # lost a race with a concurrent use
        return None
    return record.user_id
```

Why it's built this way:
- **Random tokens:** they come from `secrets.token_urlsafe(32)`, not `random`.
- **Only the hash is stored:** a database leak doesn't give anyone working reset links.
- **Single use:** `mark_used` has to be atomic in your store (for example `UPDATE ... SET used = true WHERE token_hash = ? AND used = false`, then check the row count). That stops two requests both redeeming the same token.
- **Short life:** tokens expire after 30 minutes, and issuing a new token cancels the user's previous ones.
- **Fails closed:** every failure returns `None`, and the function doesn't say *why* a token failed.
- **For whoever wires it up:**
  - Never log the raw token or the reset URL.
  - Give the same response whether or not the email exists, so the endpoint doesn't reveal which accounts exist.
  - Rate-limit the issue endpoint.
  - After a successful reset, cancel the user's sessions and hash the new password with Argon2 or bcrypt.

Tests worth adding:
- the normal flow works
- an expired token fails
- a second use fails
- an unknown or overlong token fails
- issuing a new token cancels the previous one

If you tell me where the accounts code should go (or point me to the existing user model and database layer), I can fit this to it. With write and shell access I'd then add the file and tests and run the ruff and ty checks.
