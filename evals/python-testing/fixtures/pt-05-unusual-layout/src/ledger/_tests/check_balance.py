"""Checks for ledger.balance."""

from ledger import Entry, balance
from ledger._tests import _helpers

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
    _helpers.check_values(balance(ENTRIES, "equity"), 0)
