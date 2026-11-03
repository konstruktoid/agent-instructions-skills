I didn't change anything. `balance` in `src/ledger/balance.py:4` already has a one-line docstring, `"""Return the net balance for one account."""`. I also can't edit files in this session because I only have read and search tools.

If you want it to say more about the return value, here's a fuller version you could paste in. It's based on what the code does:

```python
def balance(entries: list, account: str) -> int:
    """Return the net balance for one account.

    Sums the ``amount`` of every entry in ``entries`` whose ``account``
    matches ``account``. Positive and negative amounts cancel out, so the
    result is the net total.

    Returns:
        int: The summed amount for ``account``, or ``0`` if no entries
        match or ``entries`` is empty.
    """
    return sum(entry.amount for entry in entries if entry.account == account)
```

This only changes the docstring, so it doesn't need a new test. If you turn on file editing, I can apply it for you.
