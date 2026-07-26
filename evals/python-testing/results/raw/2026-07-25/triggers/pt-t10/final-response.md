I don't have a file-editing tool available in this session (only Read, Grep, Glob, and Skill) — I can't write the change myself. Here's the docstring I'd apply to `src/ledger/balance.py:4-6`:

```python
def balance(entries: list, account: str) -> int:
    """Return the net balance for one account.

    Returns:
        The sum of ``entry.amount`` for every entry belonging to ``account``,
        as an int (0 if the account has no matching entries).
    """
    return sum(entry.amount for entry in entries if entry.account == account)
```

Let me know if you'd like me to try again once an editing tool is available, or if you'd rather apply this yourself.
