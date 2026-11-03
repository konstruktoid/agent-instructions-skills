I can't write files in this session. The only tools I have here are read and search, with no Write, Edit or shell. So nothing has been changed in the repo, and I couldn't run `ruff`, `ty` or the tests. Two other things affect the code below:

- **There's no accounts module in the repo.** The only Python package is `src/ledger/`, so I've written this as a new `src/accounts/` package that stands on its own.
- **I couldn't read the skill's `secrets.md` reference** because permission was denied, so the design below is based on standard practice rather than that file.

### `src/accounts/__init__.py`
```python
"""Account management."""
```

### `src/accounts/reset_tokens.py`
```python
"""Issue and verify single-use password reset tokens.

A token has the form ``<selector>.<verifier>``. The selector is used to look up
the record. Only a SHA-256 digest of the verifier is stored, so a leaked
database can't be used to reset passwords. A fast hash is enough here because
the verifier is 256 bits from ``secrets``, not a password a user chose.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

DEFAULT_TTL = timedelta(minutes=30)
_SELECTOR_BYTES = 16
_VERIFIER_BYTES = 32


@dataclass(frozen=True)
class ResetRecord:
    """A stored reset token. It never holds the plaintext verifier."""

    account_id: str
    verifier_digest: bytes
    expires_at: datetime


class ResetTokenStore(Protocol):
    """Persistence for reset records, keyed by selector."""

    def put(self, selector: str, record: ResetRecord) -> None:
        """Store a record under a selector."""

    def pop(self, selector: str) -> ResetRecord | None:
        """Remove and return the record for a selector, if present."""

    def delete_for_account(self, account_id: str) -> None:
        """Remove every outstanding record for an account."""


class InMemoryResetTokenStore:
    """Dict-backed store for tests and single-process use."""

    def __init__(self) -> None:
        """Create an empty store."""
        self._records: dict[str, ResetRecord] = {}

    def put(self, selector: str, record: ResetRecord) -> None:
        """Store a record under a selector."""
        self._records[selector] = record

    def pop(self, selector: str) -> ResetRecord | None:
        """Remove and return the record for a selector, if present."""
        return self._records.pop(selector, None)

    def delete_for_account(self, account_id: str) -> None:
        """Remove every outstanding record for an account."""
        self._records = {
            s: r for s, r in self._records.items() if r.account_id != account_id
        }


def _digest(verifier: str) -> bytes:
    return hashlib.sha256(verifier.encode("ascii")).digest()


def _now() -> datetime:
    return datetime.now(UTC)


def issue_reset_token(
    store: ResetTokenStore,
    account_id: str,
    *,
    ttl: timedelta = DEFAULT_TTL,
    now: datetime | None = None,
) -> str:
    """Issue a new reset token for an account and return it.

    Any token issued earlier for the account is revoked. Send the returned
    value only to the account's verified address, and never log it.
    """
    issued_at = now or _now()
    store.delete_for_account(account_id)
    selector = secrets.token_urlsafe(_SELECTOR_BYTES)
    verifier = secrets.token_urlsafe(_VERIFIER_BYTES)
    store.put(
        selector,
        ResetRecord(
            account_id=account_id,
            verifier_digest=_digest(verifier),
            expires_at=issued_at + ttl,
        ),
    )
    return f"{selector}.{verifier}"


def verify_reset_token(
    store: ResetTokenStore,
    token: str,
    *,
    now: datetime | None = None,
) -> str | None:
    """Use up a reset token and return its account id, or ``None`` if invalid.

    The token is removed on any lookup hit, so a token works at most once,
    even after a failed check. The check fails closed: a malformed, unknown,
    expired or mismatched token returns ``None``, and callers get no hint
    about which of these it was.
    """
    selector, sep, verifier = token.partition(".")
    if not sep or not selector or not verifier or not verifier.isascii():
        return None
    record = store.pop(selector)
    if record is None:
        return None
    if not hmac.compare_digest(record.verifier_digest, _digest(verifier)):
        return None
    if (now or _now()) >= record.expires_at:
        return None
    return record.account_id
```

### `tests/test_reset_tokens.py`
```python
"""Tests for password reset tokens."""

from datetime import UTC, datetime, timedelta

from accounts.reset_tokens import (
    InMemoryResetTokenStore,
    issue_reset_token,
    verify_reset_token,
)

T0 = datetime(2026, 1, 1, tzinfo=UTC)


def test_valid_token_returns_account_once():
    """A fresh token verifies once and is then consumed."""
    store = InMemoryResetTokenStore()
    token = issue_reset_token(store, "acct-1", now=T0)
    assert verify_reset_token(store, token, now=T0) == "acct-1"
    assert verify_reset_token(store, token, now=T0) is None


def test_expired_token_rejected():
    """A token past its TTL is rejected."""
    store = InMemoryResetTokenStore()
    token = issue_reset_token(store, "acct-1", ttl=timedelta(minutes=5), now=T0)
    assert verify_reset_token(store, token, now=T0 + timedelta(minutes=5)) is None


def test_tampered_verifier_rejected():
    """A correct selector with a wrong verifier is rejected."""
    store = InMemoryResetTokenStore()
    selector, _, _ = issue_reset_token(store, "acct-1", now=T0).partition(".")
    assert verify_reset_token(store, f"{selector}.wrong", now=T0) is None


def test_reissue_revokes_previous_token():
    """Issuing a new token revokes the old one."""
    store = InMemoryResetTokenStore()
    old = issue_reset_token(store, "acct-1", now=T0)
    new = issue_reset_token(store, "acct-1", now=T0)
    assert verify_reset_token(store, old, now=T0) is None
    assert verify_reset_token(store, new, now=T0) == "acct-1"


def test_malformed_tokens_rejected():
    """Malformed input fails closed."""
    store = InMemoryResetTokenStore()
    for bad in ["", ".", "abc", "abc.", ".abc", "a.\u00e9"]:
        assert verify_reset_token(store, bad, now=T0) is None
```

### Security choices
- **Randomness:** tokens come from `secrets.token_urlsafe`, never `random`. The verifier is 256 bits.
- **Storage:** only a SHA-256 digest of the verifier is stored. A slow hash like bcrypt isn't needed because the token isn't a password a person chose.
- **Comparison:** digests are compared with `hmac.compare_digest`, which takes the same time whether or not they match. The selector/verifier split means a lookup never compares against the secret itself.
- **Single use and revocation:** a token is removed on first lookup, even if the check then fails. Issuing a new token revokes older ones for that account. The default lifetime is 30 minutes.
- **No hints:** verification returns `None` for every kind of failure. Your reset endpoint should also respond the same way whether or not the email exists, so it can't be used to find out which accounts exist.
- **Not covered here:** rate-limiting the reset request and verify endpoints, and revoking existing sessions after the password changes. Both belong in the caller.

### Still to do on your side
1. Save these files.
2. Make sure `src` is on the test path; I assume it already is, since `tests/test_balance.py` imports `ledger`.
3. Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check` and `uv run pytest`. I didn't see a `pyproject.toml` in the file listing, so these may need adapting to how the repo is actually set up.

If you give me write and shell access, I can add the files and run those checks myself.
