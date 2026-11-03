I haven't changed anything. `balance` in `src/ledger/balance.py:4` already has a one-line docstring (`"""Return the net balance for one account."""`), and I don't have a file-editing tool in this session to expand it. The Claude Docs tools that showed up only work on hosted docs, not on files in your repo.

Here's a version that spells out the return value, based on what the code does:

```python
def balance(entries: list, account: str) -> int:
    """Return the net balance for one account.

    Sums the ``amount`` of every entry in ``entries`` whose ``account``
    matches ``account``. Credits and debits are assumed to be signed
    amounts, so the result is the net total.

    Returns:
        int: The sum of matching entry amounts, or ``0`` if no entries
        match ``account`` (including when ``entries`` is empty).
    """
    return sum(entry.amount for entry in entries if entry.account == account)
```

Before you paste it in, check one thing: the line about signed amounts is my guess from the word "net" in the current docstring. The code doesn't show how debits are represented, so remove that sentence if it doesn't match your ledger. Also, the function returns a float if any `amount` is a float, even though it's annotated `-> int`.

This only changes documentation, so it doesn't need a new test.
