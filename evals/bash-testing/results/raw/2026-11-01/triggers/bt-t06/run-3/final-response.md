I couldn't create the file: this session only gives me read and search tools, with no way to write files or run commands. Below is the test file to save as `tests/test_client.py`. I haven't run it.

It follows the style of `tests/test_balance.py`: plain pytest functions, a docstring on each, and imports from `ledger.*`. The transport is replaced by a small fake that returns values from a list, so the tests don't need mocking libraries or a network.

```python
"""Tests for the ledger retrying client."""

from ledger import client
from ledger.client import MAX_ATTEMPTS, get


class FakeTransport:
    """Returns queued responses in order and records each path it was called with."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, path):
        self.calls.append(path)
        return self.responses.pop(0) if self.responses else None


def test_get_returns_first_successful_result():
    """A successful first call is returned without retrying."""
    transport = FakeTransport("body")
    assert get(transport, "/accounts") == "body"
    assert transport.calls == ["/accounts"]


def test_get_retries_until_success():
    """None results are retried until the transport returns something."""
    transport = FakeTransport(None, None, "body")
    assert get(transport, "/accounts") == "body"
    assert len(transport.calls) == 3


def test_get_passes_path_on_every_attempt():
    """Each retry asks for the same path."""
    transport = FakeTransport(None, "body")
    get(transport, "/entries/42")
    assert transport.calls == ["/entries/42", "/entries/42"]


def test_get_gives_up_after_max_attempts():
    """When every attempt fails, it returns an empty string after MAX_ATTEMPTS calls."""
    transport = FakeTransport()
    assert get(transport, "/accounts") == ""
    assert len(transport.calls) == MAX_ATTEMPTS


def test_get_does_not_exceed_max_attempts():
    """A success that would only arrive after the limit is never reached."""
    transport = FakeTransport(*([None] * MAX_ATTEMPTS), "too late")
    assert get(transport, "/accounts") == ""
    assert len(transport.calls) == MAX_ATTEMPTS


def test_get_treats_empty_string_as_success():
    """Only None counts as a failure; an empty body is returned as-is."""
    transport = FakeTransport("", "body")
    assert get(transport, "/accounts") == ""
    assert len(transport.calls) == 1


def test_get_honours_patched_max_attempts(monkeypatch):
    """The retry limit is read from the module constant at call time."""
    monkeypatch.setattr(client, "MAX_ATTEMPTS", 5)
    transport = FakeTransport()
    get(transport, "/accounts")
    assert len(transport.calls) == 5
```

To run it: `pytest tests/test_client.py`. There's no `conftest.py`, `pyproject.toml` or `pytest.ini` in the repo, so the existing `from ledger.balance import ...` only works if `src` is on the import path. Run the tests the same way you run `test_balance.py`, or use `PYTHONPATH=src pytest tests/`.

Two things in `src/ledger/client.py` you should know about. I left both out of the tests so they don't lock in behaviour that may be wrong:

- **Exceptions aren't retried.** The docstring says it retries "on transport failure", but only a `None` result triggers a retry. If the transport raises an error (a timeout, for example), it goes straight to the caller. If it should be retried, that's a code change, and then a test for it would make sense.
- **Giving up returns `""`.** After the last failed attempt it returns an empty string, so callers can't tell "all attempts failed" apart from a real empty response. That's what `test_get_treats_empty_string_as_success` shows. Raising an error or returning `None` would make the difference clear.

If you give me file-write and shell access, I can save the file and run the suite.
