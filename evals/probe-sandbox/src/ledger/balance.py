"""Compute account balances from ledger entries."""


def balance(entries: list, account: str) -> int:
    """Return the net balance for one account."""
    return sum(entry.amount for entry in entries if entry.account == account)
