I couldn't add the tests. The Write tool is disabled in this session, and I have no other way to create files, so `tests/test_client.py` doesn't exist yet.

`src/ledger/client.py` has one function, `get(transport, path)`. It calls the transport up to `MAX_ATTEMPTS` (3) times, returns the first result that isn't `None`, and returns `""` if every attempt fails. The existing `tests/test_balance.py` uses plain pytest functions with a docstring on each test and imports `from ledger.… import …`. The tests below follow that style.

I haven't run them, since the file isn't on disk. Save this as `tests/test_client.py`:

```python
"""Tests for the ledger client."""

from ledger.client import MAX_ATTEMPTS, get


def test_get_returns_first_successful_result():
    """A successful call is not retried."""
    calls = []

    def transport(path):
        calls.append(path)
        return "ok"

    assert get(transport, "/a") == "ok"
    assert calls == ["/a"]


def test_get_retries_until_success():
    """Failures (None) are retried until a result arrives."""
    results = iter([None, None, "ok"])
    calls = []

    def transport(path):
        calls.append(path)
        return next(results)

    assert get(transport, "/a") == "ok"
    assert len(calls) == 3


def test_get_returns_empty_string_after_max_attempts():
    """When every attempt fails, give up with an empty string."""
    calls = []

    def transport(path):
        calls.append(path)

    assert get(transport, "/a") == ""
    assert len(calls) == MAX_ATTEMPTS


def test_get_treats_empty_string_as_success():
    """An empty string is a result, not a failure."""
    calls = []

    def transport(path):
        calls.append(path)
        return ""

    assert get(transport, "/a") == ""
    assert len(calls) == 1
```

If you re-enable Write, or tell me another way to create files, I'll add the file and run `pytest`. Nothing in `src/ledger/balance.py` is covered beyond the one existing test, and I haven't looked at it.
