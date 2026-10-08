I didn't write the regression test. Write and Bash are both disabled in this session, so I can't create files or run anything. Nothing has been checked against the unfixed code either, and I don't know what the bug was.

**What I found**
- `src/ledger/client.py` has one function, `get(transport, path)`. It calls the transport up to `MAX_ATTEMPTS` (3) times and returns the first result that is not `None`. If every attempt returns `None`, it returns `""`.
- The only existing test is `tests/test_balance.py`. It uses plain functions, has a one-line docstring on each test, and imports `from ledger...` directly. There is no `conftest.py`, no pytest config, and no mocking library.
- I couldn't see the diff, so I'm guessing the fix. My guess is that an empty-string response used to be treated as a failure, for example with `if result:` instead of `if result is not None:`. If that's wrong, the first test below won't be a real regression test.

**Proposed `tests/test_client.py`**, in the style of `test_balance.py`:

```python
"""Tests for the ledger client retry helper."""

from ledger.client import MAX_ATTEMPTS, get


def test_get_returns_empty_response_without_retrying():
    """An empty string is a valid response, not a transport failure."""
    calls = []

    def transport(path):
        calls.append(path)
        return ""

    assert get(transport, "/empty") == ""
    assert calls == ["/empty"]


def test_get_retries_on_none_until_success():
    """None marks a transport failure and triggers a retry."""
    responses = iter([None, "ok"])
    calls = []

    def transport(path):
        calls.append(path)
        return next(responses)

    assert get(transport, "/x") == "ok"
    assert len(calls) == 2


def test_get_gives_up_after_max_attempts():
    """Persistent failure returns an empty string after MAX_ATTEMPTS tries."""
    calls = []

    def transport(path):
        calls.append(path)

    assert get(transport, "/x") == ""
    assert len(calls) == MAX_ATTEMPTS
```

The first test is the regression test. With an `if result:` check, the transport is called 3 times instead of once, so `calls == ["/empty"]` fails. The other two tests cover the retry and give-up behaviour around it.

**To finish**
1. Tell me what the bug was, or give me the diff. I'll adjust the first test to match.
2. Save the file as `tests/test_client.py`, or give me write access and I'll do it.
3. Temporarily revert the fix in `client.py` and run the suite through the project's own entry point. For example, run `uv run pytest` if the project uses uv. Confirm that `test_get_returns_empty_response_without_retrying` fails, then restore the fix.
4. Run `ruff check`, `ruff format --check` and `ty check` on the new file.
