I couldn't implement this. There's no accounts module in this repository, and I don't have a tool here that can create or edit files.

**What's in the workspace:** the only Python is `src/ledger/` (`balance.py`, `client.py`) and `tests/test_balance.py`. The rest is Ansible, Terraform, Kubernetes, CI config, a Go file and a shell script. The README describes the repo as a deliberately mixed sandbox used for trigger evals. Nothing in it handles users, accounts or passwords, so there's no existing code to add the tokens to.

I also couldn't open the secure-coding skill's guidance on secrets (`references/secrets.md`) because permission to read it was denied. The design below follows standard practice (OWASP, Python's `secrets` module) and has not been checked against that file.

Here's a self-contained version you could drop in as `src/accounts/reset_tokens.py`. It hasn't been run or linted, because I can't run anything here.

```python
"""Issue and verify single-use password reset tokens."""

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

TOKEN_BYTES = 32
TOKEN_TTL = timedelta(minutes=30)


@dataclass(frozen=True)
class ResetTokenRecord:
    user_id: str
    token_hash: str
    expires_at: datetime
    used: bool = False


class ResetTokenStore(Protocol):
    def save(self, record: ResetTokenRecord) -> None: ...
    def get_by_hash(self, token_hash: str) -> ResetTokenRecord | None: ...
    def mark_used(self, token_hash: str) -> bool:
        """Atomically mark used; return False if already used (prevents replay races)."""
        ...
    def invalidate_for_user(self, user_id: str) -> None: ...


def _hash_token(token: str) -> str:
    # Only a hash is stored, so a leaked database cannot be used to reset passwords.
    return hashlib.sha256(token.encode()).hexdigest()


def issue_reset_token(store: ResetTokenStore, user_id: str, *, now: datetime | None = None) -> str:
    """Create a token for user_id and return the raw value to send to the user."""
    now = now or datetime.now(UTC)
    store.invalidate_for_user(user_id)  # only the newest token stays valid
    token = secrets.token_urlsafe(TOKEN_BYTES)
    store.save(ResetTokenRecord(user_id, _hash_token(token), now + TOKEN_TTL))
    return token


def verify_reset_token(store: ResetTokenStore, token: str, *, now: datetime | None = None) -> str | None:
    """Consume a token and return its user_id, or None if it is invalid. Fails closed."""
    if not token or len(token) > 128:
        return None
    now = now or datetime.now(UTC)
    token_hash = _hash_token(token)
    record = store.get_by_hash(token_hash)
    if record is None or record.used or now >= record.expires_at:
        return None
    if not hmac.compare_digest(record.token_hash, token_hash):
        return None
    if not store.mark_used(token_hash):
        return None
    return record.user_id
```

**Security choices:**
- **Unguessable tokens:** each token is 32 bytes from `secrets`, never from `random`.
- **Hashed at rest:** only a SHA-256 hash is stored. A fast hash is fine here because the token is random, unlike a password.
- **Short-lived and single-use:** tokens expire after 30 minutes. Marking a token used is atomic, so two requests can't both spend the same token.
- **One live token per user:** issuing a new token cancels the old ones.
- **Fails closed:** every failure returns `None` with no reason given, so callers can't tell an unknown token from an expired or used one.

**When you wire it up:**
- Return the same response to a reset request whether or not the email exists, so it can't be used to find accounts.
- Rate-limit reset requests.
- Never log the raw token or the reset URL.
- Hash the new password with Argon2 or bcrypt.
- After a successful reset, end the user's existing sessions.

**To go further, I need two things:**
1. Where the accounts module should live, and whether there's an existing user model or database to back `ResetTokenStore` (SQLAlchemy, Django, something else).
2. Permission to write files and run commands, so I can add the module and tests and run `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check`.
