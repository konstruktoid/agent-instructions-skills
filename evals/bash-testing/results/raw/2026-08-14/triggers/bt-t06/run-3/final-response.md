I don't have file-write access in this session (only Glob, Grep, Read, and Skill are available — no Write, Edit, or Bash), so I can't create `tests/test_client.py` directly. Here's the content to add, matching the existing style in `tests/test_balance.py`:

```python
"""Tests for the ledger client's retry behavior."""

from ledger.client import MAX_ATTEMPTS, get


def test_get_returns_first_successful_result():
    """No retry is needed when the transport succeeds immediately."""
    calls = []

    def transport(path):
        calls.append(path)
        return f"ok:{path}"

    assert get(transport, "/accounts") == "ok:/accounts"
    assert calls == ["/accounts"]


def test_get_retries_after_transport_failure():
    """A single failure is retried and the next success is returned."""
    results = iter([None, "ok"])

    def transport(path):
        return next(results)

    assert get(transport, "/accounts") == "ok"


def test_get_returns_empty_string_after_exhausting_retries():
    """Once every attempt fails, an empty string is returned instead of raising."""
    calls = []

    def transport(path):
        calls.append(path)
        return None

    assert get(transport, "/accounts") == ""
    assert len(calls) == MAX_ATTEMPTS
```

Save it as `tests/test_client.py` and it should run alongside `tests/test_balance.py`. Let me know if you'd like me to try again once file-write tools are available.
