I wrote a draft test below, but I couldn't save it, run it, or confirm that it fails against the unfixed code. I only have read and search tools here: nothing to write files, run `pytest`, or view git history.

**What I could check**

- `src/ledger/client.py` contains only the current code. `get()` calls `transport(path)` up to `MAX_ATTEMPTS` (3) times, retries when the result is `None`, and returns `""` once the attempts run out.
- Without `git diff` or `git log`, I can't see the old code, so I don't know exactly what the fix changed.
- The existing tests are in `tests/test_<module>.py`. They are plain functions with a docstring each, import from `ledger.<module>`, and have no `conftest.py`, fixtures or mocking library. The draft follows that style and uses a small hand-written fake transport.

**Draft for `tests/test_client.py`**

```python
"""Tests for the ledger retrying client."""

from ledger.client import MAX_ATTEMPTS, get


def _flaky(failures: int, value: str = "ok"):
    """Return a transport that returns None `failures` times, then `value`."""
    calls: list[str] = []

    def transport(path: str):
        calls.append(path)
        return None if len(calls) <= failures else value

    return transport, calls


def test_get_succeeds_on_last_allowed_attempt():
    """A transport that recovers on the final attempt is retried until it does."""
    transport, calls = _flaky(failures=MAX_ATTEMPTS - 1)
    assert get(transport, "/accounts") == "ok"
    assert len(calls) == MAX_ATTEMPTS


def test_get_gives_up_after_max_attempts():
    """A transport that never recovers is called exactly MAX_ATTEMPTS times."""
    transport, calls = _flaky(failures=MAX_ATTEMPTS + 5)
    assert get(transport, "/accounts") == ""
    assert calls == ["/accounts"] * MAX_ATTEMPTS
```

I'm assuming the fix was about how many times `get()` retries. The first test fails if the old code didn't retry at all or stopped one attempt early. The second fails if it retried too many times or forever. If the fix was something else, this test may pass against the old code too and won't catch the regression. For example, the docstring says "retrying on transport failure", and if the fix was about the transport raising an exception, the current code doesn't catch exceptions at all.

**What I still need from you**

1. Tell me what the fix changed, or paste the output of `git diff` for `client.py`, so I can confirm the test targets it.
2. Save the test, then:
   - Stash the fix and run `pytest tests/test_client.py`. It should fail.
   - Restore the fix and run `pytest`. The whole suite should pass.
   - Run `ruff check`, `ruff format --check` and `ty check` on the new file.

If you send me the diff or those results, I'll adjust the test.
