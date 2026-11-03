I couldn't finish this, for two reasons:

1. **I can't see the fix.** I don't have shell access in this session, so I couldn't run `git diff` or `git log`. All I can see is the current `src/ledger/client.py`. A regression test has to target the specific bug, and I'd only be guessing which one it was.
2. **I can't write or run anything.** I only have read and search tools here, so I couldn't create the test file or show that it fails without the fix.

**What's in the repo now:**
- `src/ledger/client.py:6`: `get()` calls `transport(path)` up to `MAX_ATTEMPTS` (3) times. It retries when the result is `None` and returns `""` if every attempt fails.
- `tests/test_balance.py` is the only existing test. It uses plain pytest functions, a module docstring, a one-line docstring on each test, and no mocking library.
- There's no `pyproject.toml`, `pytest.ini` or `setup.cfg`, so the `from ledger...` import only works with `src` on the path (e.g. `PYTHONPATH=src pytest`).

**A draft for `tests/test_client.py`**, written in the same style and assuming the fix was to the retry loop (for example, it used to give up after the first `None`, or tried the wrong number of times):

```python
"""Tests for the ledger retrying client."""

from ledger.client import MAX_ATTEMPTS, get


def test_get_retries_until_transport_succeeds():
    """A None result is retried and the first real result is returned."""
    results = iter([None, None, "ok"])
    calls = []

    def transport(path):
        calls.append(path)
        return next(results)

    assert get(transport, "/acct") == "ok"
    assert calls == ["/acct"] * 3


def test_get_gives_up_after_max_attempts():
    """A transport that never succeeds is tried exactly MAX_ATTEMPTS times."""
    calls = []

    def transport(path):
        calls.append(path)
        return None

    assert get(transport, "/acct") == ""
    assert len(calls) == MAX_ATTEMPTS
```

Counting calls is fine here because the number of retries is the behaviour being fixed.

**One more possible bug:** the docstring says it retries "on transport failure", but if `transport` raises an exception, `get()` doesn't retry at all. If the fix was meant to cover exceptions, that change isn't in the file. The test would need to make `transport` raise and then succeed, and it would fail against the current code.

**To finish this, I need:**
- The diff, or a one-line description of what was broken.
- Shell and write access, or you can run it yourself: revert `client.py` to before the fix, run `PYTHONPATH=src pytest tests/test_client.py` and confirm it fails, then restore the fix and run the whole suite to confirm it passes.
