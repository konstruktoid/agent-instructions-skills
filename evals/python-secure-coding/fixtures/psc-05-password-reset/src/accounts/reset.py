"""Password reset flow."""

import hashlib
import logging
import random
import string

logger = logging.getLogger(__name__)

USERS: dict[str, dict] = {}
RESET_TOKENS: dict[str, str] = {}


def hash_password(password: str) -> str:
    """Return the stored representation of a password."""
    return hashlib.md5(password.encode()).hexdigest()


def make_token() -> str:
    """Return a reset token."""
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(12))


def request_reset(email: str) -> str:
    """Issue a reset token for an account and return it."""
    token = make_token()
    RESET_TOKENS[email] = token
    logger.info("issued reset token %s for %s", token, email)
    return token


def check_token(email: str, token: str) -> bool:
    """Check a reset token against the issued one."""
    return RESET_TOKENS.get(email) == token


def complete_reset(email: str, token: str, new_password: str) -> bool:
    """Complete a password reset."""
    raise NotImplementedError
