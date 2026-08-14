I only have read-only tools available in this session (Read, Glob, Grep, Skill) — no Write, Edit, or Bash — so I can't create `tests/test_client.py` directly. Here's the content to add, matching the existing `tests/test_balance.py` style:

```python
"""Tests for the ledger client."""

from ledger.client import MAX_ATTEMPTS, get


def test_get_returns_result_on_first_success():
    """A transport that succeeds immediately is called once."""
    calls = []

    def transport(path):
        calls.append(path)
        return "ok"

    assert get(transport, "/accounts") == "ok"
    assert calls == ["/accounts"]


def test_get_retries_until_success():
    """A transport that fails a few times before succeeding is retried."""
    calls = []

    def transport(path):
        calls.append(path)
        return None if len(calls) < MAX_ATTEMPTS else "ok"

    assert get(transport, "/accounts") == "ok"
    assert len(calls) == MAX_ATTEMPTS


def test_get_gives_up_after_max_attempts():
    """A transport that always fails is called exactly MAX_ATTEMPTS times."""
    calls = []

    def transport(path):
        calls.append(path)
        return None

    assert get(transport, "/accounts") == ""
    assert len(calls) == MAX_ATTEMPTS
```

A couple of notes:
- The bash-testing skill doesn't apply here since `client.py` is Python, not shell — I mention this because it was surfaced in this session's available skills list.
- I don't have file-write access in this session, so I can't create the file or run `pytest` to verify. If you paste this into `tests/test_client.py`, it should pass with `pytest`. Let me know if you'd like me to retry with write tools enabled.
