I couldn't add the docstring because the Edit tool is disabled in this session, so `src/ledger/balance.py` is unchanged. I didn't try another way to write the file.

`balance` already has a one-line docstring: `"""Return the net balance for one account."""`. I wanted to expand it like this:

```python
def balance(entries: list, account: str) -> int:
    """Return the net balance for one account.

    Sums the amount of every entry whose account matches ``account``, so
    credits and debits offset each other. Returns 0 when no entry matches.
    """
    return sum(entry.amount for entry in entries if entry.account == account)
```

You can paste that in yourself. If you enable Edit, I'll make the change.
