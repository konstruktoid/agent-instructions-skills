I couldn't add the tests. The Write tool is disabled in this session, and I have no other way to create files here. I haven't run anything.

This is the file I would have created at `tests/test_client.py`. It matches the style of `tests/test_balance.py`:

```python
"""Tests for the ledger client."""

from ledger.client import MAX_ATTEMPTS, get


def make_transport(responses):
    """Return a transport yielding the given responses, recording calls."""
    calls = []
    queue = iter(responses)

    def transport(path):
        calls.append(path)
        return next(queue)

    transport.calls = calls
    return transport


def test_get_returns_first_success_without_retrying():
    """A successful first call is returned and not repeated."""
    transport = make_transport(["ok"])
    assert get(transport, "/a") == "ok"
    assert transport.calls == ["/a"]


def test_get_retries_after_failure():
    """A None result triggers another attempt."""
    transport = make_transport([None, None, "ok"])
    assert get(transport, "/a") == "ok"
    assert transport.calls == ["/a"] * 3


def test_get_returns_empty_string_after_max_attempts():
    """Persistent failure gives up after MAX_ATTEMPTS and returns ''."""
    transport = make_transport([None] * MAX_ATTEMPTS)
    assert get(transport, "/a") == ""
    assert len(transport.calls) == MAX_ATTEMPTS


def test_get_treats_empty_string_as_success():
    """Only None counts as failure; '' is returned immediately."""
    transport = make_transport([""])
    assert get(transport, "/a") == ""
    assert transport.calls == ["/a"]
```

- **Setup:** I found no pytest config or `PYTHONPATH` setting in the repo. `test_balance.py` imports `ledger.balance` directly, so I assumed `src` is already on the path. I couldn't check that.
- **Coverage:** `src/ledger/client.py` only has `get`, so the tests cover success on the first try, retry then success, giving up after `MAX_ATTEMPTS`, and `""` counting as success.
- **Not covered:** `src/ledger/balance.py` already has a test file, so I left it alone.

If you enable Write, or paste the file in yourself, I can run `pytest` and fix any failures.
