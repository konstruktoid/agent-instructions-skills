I couldn't make this change because I don't have a tool that can edit files in this session. I can only read and search. Here's the docstring to paste in. It replaces the one-line docstring now at `src/ledger/balance.py:5`:

```python
def balance(entries: list, account: str) -> int:
    """Return the net balance for one account.

    Adds up the ``amount`` of every entry in ``entries`` whose ``account``
    matches ``account``. Amounts are added with their signs, so credits
    and debits cancel out.

    Args:
        entries: Ledger entries, each with ``account`` and ``amount``
            attributes.
        account: The account to total.

    Returns:
        The sum of the matching entries' amounts as an ``int``. Returns
        ``0`` if no entries match or if ``entries`` is empty.
    """
    return sum(entry.amount for entry in entries if entry.account == account)
```

The description of what it returns comes straight from the code: `sum()` of an empty sequence is `0`, so an unknown account gives `0` rather than raising an error. This only changes a docstring, so it doesn't need a new test.
