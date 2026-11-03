I couldn't create the test file because I don't have a tool that writes files or runs commands in this session. Here is the file to save as `tests/test_client.py`. It follows the existing `tests/test_balance.py`: plain pytest functions, one docstring each, importing from `ledger.*`. I haven't run it.

```python
"""Tests for the ledger retrying client."""

import pytest

from ledger.client import MAX_ATTEMPTS, get


class FakeTransport:
    """Return queued responses in order and record each path requested."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, path):
        self.calls.append(path)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_get_returns_first_successful_result():
    """A successful first call is returned without retrying."""
    transport = FakeTransport("ok")
    assert get(transport, "/accounts") == "ok"
    assert transport.calls == ["/accounts"]


def test_get_retries_after_none_then_succeeds():
    """A None result is treated as a failure and retried."""
    transport = FakeTransport(None, None, "ok")
    assert get(transport, "/accounts") == "ok"
    assert len(transport.calls) == 3


def test_get_passes_path_on_every_attempt():
    """Every retry requests the same path."""
    transport = FakeTransport(None, "ok")
    get(transport, "/ledger/42")
    assert transport.calls == ["/ledger/42", "/ledger/42"]


def test_get_returns_empty_string_after_max_attempts():
    """It gives up after MAX_ATTEMPTS failures and returns an empty string."""
    transport = FakeTransport(*([None] * MAX_ATTEMPTS))
    assert get(transport, "/accounts") == ""
    assert len(transport.calls) == MAX_ATTEMPTS


def test_get_does_not_exceed_max_attempts():
    """A success queued after the limit is never reached."""
    transport = FakeTransport(*([None] * MAX_ATTEMPTS), "too late")
    assert get(transport, "/accounts") == ""
    assert len(transport.calls) == MAX_ATTEMPTS


def test_get_returns_empty_string_result_without_retry():
    """An empty string counts as success, because only None triggers a retry."""
    transport = FakeTransport("")
    assert get(transport, "/accounts") == ""
    assert len(transport.calls) == 1


def test_get_propagates_transport_exceptions():
    """Exceptions are not retried; they reach the caller on the first attempt."""
    transport = FakeTransport(ConnectionError("down"), "ok")
    with pytest.raises(ConnectionError):
        get(transport, "/accounts")
    assert len(transport.calls) == 1
```

To run it: `PYTHONPATH=src pytest tests/`. The repo has no `pyproject.toml` or `conftest.py`, so the existing tests already seem to rely on `src` being on the path.

**Behaviour these tests lock in that you may not want:**
- **Exceptions aren't retried.** The docstring in `src/ledger/client.py` says it retries "on transport failure", but `get` only retries when the transport returns `None`. A raised exception stops it on the first attempt. The last test pins that. If exceptions should be retried, fix `get` first and change that test.
- **The caller can't tell two outcomes apart.** Giving up after three failures returns `""`, which is the same as a successful empty response. The two empty-string tests show this.
