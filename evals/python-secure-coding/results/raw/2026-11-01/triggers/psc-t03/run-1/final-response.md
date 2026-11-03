I couldn't make this change. This session has no tool for writing or editing files, and the repository has no accounts module. The only Python code is in `src/ledger/` (`balance.py`, `client.py`, and `tests/test_balance.py`). I also couldn't run `ruff`, `ty`, or tests, and I wasn't given permission to read the skill's `references/secrets.md`, so the code below follows standard practice for tokens rather than that file.

Here's an implementation you can drop in at `src/accounts/reset_tokens.py`. It matches the existing style: plain functions, docstrings, and the storage passed in as a parameter, the way `client.get` takes `transport`.

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
    """Stored reset state; holds only a hash of the token, never the token itself."""

    user_id: str
    token_hash: str
    expires_at: datetime


class ResetStore(Protocol):
    """Persistence for reset records, keyed by token hash."""

    def put(self, record: ResetRecord) -> None: ...
    def delete_for_user(self, user_id: str) -> None: ...
    def pop(self, token_hash: str) -> ResetRecord | None:
        """Atomically fetch and delete, so a token can be redeemed only once."""
        ...


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue(store: ResetStore, user_id: str, now: datetime | None = None) -> str:
    """Create a reset token for user_id, revoking any earlier ones.

    Returns the plaintext token to send to the user out of band (e.g. email link).
    """
    now = now or datetime.now(UTC)
    token = secrets.token_urlsafe(TOKEN_BYTES)
    store.delete_for_user(user_id)
    store.put(ResetRecord(user_id, _hash(token), now + TOKEN_TTL))
    return token


def verify(store: ResetStore, token: str, now: datetime | None = None) -> str | None:
    """Consume a token; return its user_id if valid and unexpired, else None."""
    now = now or datetime.now(UTC)
    if not token or len(token) > 128:
        return None
    token_hash = _hash(token)
    record = store.pop(token_hash)
    if record is None:
        return None
    if not secrets.compare_digest(record.token_hash, token_hash):
        return None
    if now >= record.expires_at:
        return None
    return record.user_id
```

**How it handles security:**
- **Randomness:** tokens use `secrets.token_urlsafe(32)` (256 bits), never `random`.
- **Hash at rest:** the store only ever holds a SHA-256 hash, so a leaked database can't be used to reset passwords. A fast hash is fine here because the token is already high-entropy; slow hashes like bcrypt are only needed for low-entropy secrets such as passwords.
- **Single use:** `pop` must fetch and delete in one step (for example, SQL `DELETE … RETURNING`). Otherwise two requests racing with the same token could both succeed.
- **One live token per user:** issuing a new token deletes the user's earlier ones.
- **Fails closed:** any problem (empty, too long, unknown, or expired token) returns `None`. Expired tokens are still removed when someone tries them. `verify` returns the same `None` in every case, so callers can't tell an unknown token from an expired one.
- **Time is injectable:** passing `now` makes expiry testable without mocking the clock.
- **Callers must:** never log the token, send the reset email only to the address already on file, and show the same response whether or not the account exists, so the reset form doesn't reveal which accounts are registered.

**Tests to add:** issue then verify returns the user ID; a second verify returns `None`; verifying at `now + TOKEN_TTL` returns `None`; issuing again makes the first token invalid; tampered or empty tokens return `None`. Then run `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check`, and `pytest`.

If the accounts code lives in another repository or branch, point me to it. Or, if you can enable file editing, I'll write this and the tests in and run the checks myself.
