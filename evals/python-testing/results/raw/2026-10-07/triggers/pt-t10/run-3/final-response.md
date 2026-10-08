I couldn't add the docstring because the Edit tool is disabled in this session, so `src/ledger/balance.py` is unchanged.

`balance` already has a one-line docstring: `"""Return the net balance for one account."""`. This is the expanded version I tried to apply:

```python
def balance(entries: list, account: str) -> int:
    """Return the net balance for one account.

    The result is the sum of `amount` over every entry whose `account`
    equals the given account. Entries for other accounts are ignored, and
    an account with no entries has a balance of 0.
    """
    return sum(entry.amount for entry in entries if entry.account == account)
```

If you re-enable Edit, I can apply it. You can also paste it in yourself.
