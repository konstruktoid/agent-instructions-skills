"""Checks for ledger.balance."""

from ledger import Entry, balance

ENTRIES = [
    Entry("cash", 100),
    Entry("cash", -30),
    Entry("receivable", 50),
]


def check_balance_sums_one_account():
    """Entries for other accounts are ignored."""
    assert balance(ENTRIES, "cash") == 70


def check_balance_of_an_unknown_account_is_zero():
    """An account with no entries has a zero balance."""
    assert balance(ENTRIES, "equity") == 0
