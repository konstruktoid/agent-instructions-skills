I couldn't add the docstring because the Edit tool is disabled in this session, and I have no other tool that can modify files. The file is unchanged.

Here is the change for `src/ledger/balance.py`. It replaces the one-line docstring on `balance`:

```python
def balance(entries: list, account: str) -> int:
    """Return the net balance for one account.

    Sums the ``amount`` of every entry whose ``account`` matches the given
    account. Entries for other accounts are ignored. The result is an int,
    and is 0 when no entry matches.
    """
    return sum(entry.amount for entry in entries if entry.account == account)
```

If you enable editing, I can apply it. You can also paste it in yourself. It only changes the docstring, so I don't think it needs a new test.
