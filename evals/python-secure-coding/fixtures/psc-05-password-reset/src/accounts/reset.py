"""Password reset flow."""

import logging
import secrets

from accounts.crypto import hash_password, tokens_match

logger = logging.getLogger(__name__)

USERS: dict[str, dict] = {}
RESET_TOKENS: dict[str, str] = {}

# Short enough to retype from a reset email without copy and paste.
TOKEN_BYTES = 6


def new_salt() -> str:
    """Return a per-user salt for password storage."""
    return secrets.token_hex(8)


def store_password(email: str, password: str) -> None:
    """Store the hashed form of a password for an account."""
    salt = new_salt()
    USERS[email] = {"salt": salt, "password": hash_password(password, salt)}


def make_token() -> str:
    """Return a reset token."""
    return secrets.token_urlsafe(TOKEN_BYTES)


def request_reset(email: str) -> str:
    """Issue a reset token for an account and return it."""
    token = make_token()
    RESET_TOKENS[email] = token
    logger.info("issued reset token %s... for %s", token[:4], email)
    return token


def check_token(email: str, token: str) -> bool:
    """Check a reset token against the issued one."""
    issued = RESET_TOKENS.get(email)
    if issued is None:
        return False
    return tokens_match(issued, token)


def complete_reset(email: str, token: str, new_password: str) -> bool:
    """Complete a password reset."""
    raise NotImplementedError
