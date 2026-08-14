I don't have write access to the filesystem in this session (no Edit/Write/Bash tool available — only Read, Glob, Grep, and Skill). I can't create `tests/test_client.py` directly.

Here's the test file I'd add, matching the style of the existing `tests/test_balance.py`:

```python
"""Tests for the ledger client's retrying transport call."""

from ledger.client import MAX_ATTEMPTS, get


def test_get_returns_result_on_first_success():
    """A transport that succeeds immediately is called once."""
    calls = []

    def transport(path):
        calls.append(path)
        return "ok"

    assert get(transport, "/balance") == "ok"
    assert calls == ["/balance"]


def test_get_retries_until_success():
    """A transport that fails a few times is retried with the same path."""
    calls = []

    def transport(path):
        calls.append(path)
        return None if len(calls) < MAX_ATTEMPTS else "ok"

    assert get(transport, "/balance") == "ok"
    assert calls == ["/balance"] * MAX_ATTEMPTS


def test_get_gives_up_after_max_attempts():
    """A transport that always fails is called exactly MAX_ATTEMPTS times."""
    calls = []

    def transport(path):
        calls.append(path)
        return None

    assert get(transport, "/balance") == ""
    assert len(calls) == MAX_ATTEMPTS
```

Could you either grant file-write permission for this session or paste this into `tests/test_client.py` yourself?
