"""Compute account balances from ledger entries."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    """One ledger entry against a named account."""

    account: str
    amount: int


def balance(entries: list, account: str) -> int:
    """Return the net balance for one account."""
    return sum(entry.amount for entry in entries if entry.account == account)
