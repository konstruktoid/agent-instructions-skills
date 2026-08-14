I found `src/ledger/client.py` (a retrying transport wrapper) and the existing `tests/test_balance.py` for style reference — plain pytest, no fixtures/mocking libs, one behavior per test. This is a pure Python/pytest task, not a Bash one, so no skill applies here.

However, I don't have file-write tools available in this session (only Glob/Grep/Read/Skill), so I can't create `tests/test_client.py` directly. Here's the test file matching the repo's existing conventions — please add it manually, or let me know if you'd like to adjust anything first:

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
    """A transport that fails then succeeds is retried."""
    calls = []

    def transport(path):
        calls.append(path)
        return None if len(calls) < 2 else "ok"

    assert get(transport, "/accounts") == "ok"
    assert len(calls) == 2


def test_get_gives_up_after_max_attempts():
    """A transport that always fails is retried MAX_ATTEMPTS times then gives up."""
    calls = []

    def transport(path):
        calls.append(path)
        return None

    assert get(transport, "/accounts") == ""
    assert len(calls) == MAX_ATTEMPTS
```

Covers: immediate success (one call), success after retrying, and exhausting `MAX_ATTEMPTS` returning `""`.
