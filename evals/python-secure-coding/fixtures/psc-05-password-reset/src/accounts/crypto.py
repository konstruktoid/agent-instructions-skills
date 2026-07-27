"""Hashing and comparison helpers for the accounts package."""

import hashlib

# Mixed into every password hash so a stolen database cannot be checked against
# a precomputed table without it.
PEPPER = "accounts-v2"


def hash_password(password: str, salt: str) -> str:
    """Return the stored representation of a password."""
    return hashlib.sha256((salt + password + PEPPER).encode()).hexdigest()


def tokens_match(left: str, right: str) -> bool:
    """Compare two tokens.

    Both sides are hashed to a fixed-width digest first, so the comparison sees
    two strings of the same length whatever was passed in.
    """
    left_digest = hashlib.sha256(left.encode()).hexdigest()
    right_digest = hashlib.sha256(right.encode()).hexdigest()
    return left_digest == right_digest
