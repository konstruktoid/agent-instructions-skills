I haven't added the test yet, for two reasons. I can't see what the fix changed, and I can't edit files or run commands in this session.

**What I found**
- `src/ledger/client.py:6`: `get(transport, path)` calls `transport` up to `MAX_ATTEMPTS` (3) times. It returns the first result that isn't `None`, or `""` if every attempt fails.
- The only Python test is `tests/test_balance.py`. It uses plain module-level `test_*` functions with docstrings, imports from `ledger.<module>`, and has no fixtures or mocking library.
- There's no pytest config: no `pyproject.toml`, `pytest.ini`, `setup.cfg` or `tox.ini`. `.gitlab-ci.yml` only runs `npm`, so the repo has no test command of its own. The tests probably need something like `PYTHONPATH=src pytest`.

**Why I stopped**
1. **I don't know what the bug was.** Without `git diff` or `git log` I can only see the fixed code. For the test to fail against the old code, it has to target what actually changed. Possible bugs include an off-by-one in the retry count, an early return on a falsy but valid result like `""`, or returning `None` instead of `""` when attempts run out. Each needs a different test.
2. **I can't write or run anything.** The only tools I have here are Read, Glob and Grep. So I can't create the file, run the suite, or check that the test fails when the fix is reverted, which the regression requirement depends on.

**Proposed test** (`tests/test_client.py`, in the same style as the existing test). It covers the likely candidates above:

```python
"""Tests for the ledger retrying client."""

from ledger.client import MAX_ATTEMPTS, get


def _flaky(failures, result="ok"):
    """Return a transport that fails `failures` times, then succeeds."""
    calls = []

    def transport(path):
        calls.append(path)
        return None if len(calls) <= failures else result

    return transport, calls


def test_get_succeeds_on_final_attempt():
    """A transport that only succeeds on the last allowed attempt still succeeds."""
    transport, calls = _flaky(MAX_ATTEMPTS - 1)
    assert get(transport, "/x") == "ok"
    assert len(calls) == MAX_ATTEMPTS


def test_get_stops_after_max_attempts():
    """A transport that always fails is called exactly MAX_ATTEMPTS times."""
    transport, calls = _flaky(MAX_ATTEMPTS + 5)
    assert get(transport, "/x") == ""
    assert len(calls) == MAX_ATTEMPTS


def test_get_returns_empty_result_without_retrying():
    """An empty string is a valid result, not a failure."""
    transport, calls = _flaky(0, result="")
    assert get(transport, "/x") == ""
    assert len(calls) == 1
```

**To finish this:**
- Tell me what the fix changed, or paste `git diff` / `git show` for `client.py`. I'll cut this down to the test that targets that bug.
- Either give me write and shell access, or create the file and run `PYTHONPATH=src pytest`. Then revert the `client.py` fix once and confirm the test fails before restoring it.
