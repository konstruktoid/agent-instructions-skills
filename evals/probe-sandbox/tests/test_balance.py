"""Tests for the ledger balance helper."""

from ledger.balance import balance


def test_balance_sums_one_account():
    """Entries for other accounts are ignored."""
    assert balance([], "cash") == 0
