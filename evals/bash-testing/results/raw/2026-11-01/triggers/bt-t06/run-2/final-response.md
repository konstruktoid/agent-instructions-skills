I couldn't create the file. This session only gives me read and search tools, with no way to write files or run commands. So nothing has been added or run yet. Here's the test file, based on `src/ledger/client.py` and written to match the style of `tests/test_balance.py`. Save it as `tests/test_client.py`:

```python
"""Tests for the ledger retrying client."""

import pytest

from ledger import client
from ledger.client import MAX_ATTEMPTS, get


class FakeTransport:
    """Returns queued results in order and records each path it was called with."""

    def __init__(self, *results):
        self.results = list(results)
        self.calls = []

    def __call__(self, path):
        self.calls.append(path)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_get_returns_first_successful_result_without_retrying():
    """A result on the first try stops the retries."""
    transport = FakeTransport("body")
    assert get(transport, "/accounts") == "body"
    assert transport.calls == ["/accounts"]


def test_get_retries_after_none_then_returns_result():
    """None counts as a failure and triggers another attempt."""
    transport = FakeTransport(None, None, "body")
    assert get(transport, "/accounts") == "body"
    assert transport.calls == ["/accounts"] * 3


def test_get_gives_up_after_max_attempts_and_returns_empty_string():
    """When every attempt fails, it stops after MAX_ATTEMPTS and returns ''."""
    transport = FakeTransport(*([None] * (MAX_ATTEMPTS + 1)))
    assert get(transport, "/accounts") == ""
    assert len(transport.calls) == MAX_ATTEMPTS


def test_get_respects_patched_max_attempts(monkeypatch):
    """The retry limit is read from the module constant when get() is called."""
    monkeypatch.setattr(client, "MAX_ATTEMPTS", 1)
    transport = FakeTransport(None, "body")
    assert get(transport, "/accounts") == ""
    assert transport.calls == ["/accounts"]


@pytest.mark.parametrize("falsy", ["", 0, [], False])
def test_get_treats_falsy_non_none_result_as_success(falsy):
    """Only None means failure. Other falsy results are returned right away."""
    transport = FakeTransport(falsy)
    assert get(transport, "/accounts") == falsy
    assert len(transport.calls) == 1


def test_get_does_not_catch_transport_exceptions():
    """An exception from the transport goes straight to the caller with no retry."""
    transport = FakeTransport(ConnectionError("down"), "body")
    with pytest.raises(ConnectionError):
        get(transport, "/accounts")
    assert len(transport.calls) == 1
```

**Things to know:**

- **Running the tests:** the repo has no `pyproject.toml`, `conftest.py` or pytest config. The existing test imports `ledger.balance`, so I'm assuming you run tests with `src` on the import path, e.g. `PYTHONPATH=src pytest tests/`.
- **Two tests lock in behavior you may not want:**
  - A transport that returns `""` is indistinguishable from one that failed every attempt, because `get()` returns `""` in both cases.
  - Exceptions from the transport aren't retried, even though the docstring says it retries "on transport failure".

  If either is a bug, tell me and I'll change those tests to expect the fixed behavior.

Once I can write files, I can add this and run it myself. Or, if you'd like me to make changes, paste back what `pytest` reports.
