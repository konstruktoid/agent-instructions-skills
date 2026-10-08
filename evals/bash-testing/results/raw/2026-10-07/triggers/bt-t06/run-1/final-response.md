I couldn't create `tests/test_client.py`. The Write tool is disabled in this session, and I have no other way to create files. Nothing has been written or run.

This is the file I would add. It follows the style of `tests/test_balance.py` (module docstring, one docstring per test, plain asserts):

```python
"""Tests for the ledger client."""

from ledger.client import MAX_ATTEMPTS, get


def make_transport(responses):
    """Return a transport yielding the given responses and recording calls."""
    calls = []
    remaining = iter(responses)

    def transport(path):
        calls.append(path)
        return next(remaining)

    transport.calls = calls
    return transport


def test_get_returns_first_success_without_retry():
    """A successful first call is not retried."""
    transport = make_transport(["ok"])
    assert get(transport, "/a") == "ok"
    assert transport.calls == ["/a"]


def test_get_retries_after_failure():
    """None results are retried until one succeeds."""
    transport = make_transport([None, None, "ok"])
    assert get(transport, "/a") == "ok"
    assert transport.calls == ["/a"] * 3


def test_get_gives_up_after_max_attempts():
    """Persistent failure returns an empty string after MAX_ATTEMPTS calls."""
    transport = make_transport([None] * MAX_ATTEMPTS)
    assert get(transport, "/a") == ""
    assert len(transport.calls) == MAX_ATTEMPTS


def test_get_treats_empty_string_as_success():
    """An empty string is a valid result, not a failure."""
    transport = make_transport(["", "ok"])
    assert get(transport, "/a") == ""
    assert len(transport.calls) == 1
```

- **What it covers:** `ledger.client.get` returns on the first success, retries on `None`, gives up after `MAX_ATTEMPTS` with `""`, and treats `""` as a success.
- **Import path:** I found no `pyproject.toml`, `pytest.ini`, `conftest.py` or `PYTHONPATH` setting. `tests/test_balance.py` imports `ledger.balance` the same way, so `from ledger.client import ...` should resolve whenever that test does. I haven't confirmed that.

If you enable Write, or tell me to create the file another way, I'll add it and run `pytest`.
