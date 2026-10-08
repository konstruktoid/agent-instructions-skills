I haven't written the test. Write and Bash are both disabled in this session, so I can't create the file, check that it fails against the unfixed code, or run the suite.

**I also don't know which bug you fixed.** The repo has no diff for me to read, and `client.py` is the only place the fix could be. The only candidate I can see is `src/ledger/client.py:10`, `if result is not None`. That looks like the result of changing a truthiness check (`if result:`) so that an empty-string response isn't treated as a failure and retried. If your fix was something else, the test below won't be the right one.

I matched the existing style in `tests/test_balance.py`: plain functions, a docstring on each, no fixtures or mocks. This is the proposed `tests/test_client.py`:

```python
"""Tests for the ledger client."""

from ledger.client import MAX_ATTEMPTS, get


def test_get_does_not_retry_an_empty_response():
    """An empty string is a valid response, not a transport failure."""
    calls = []

    def transport(path):
        calls.append(path)
        return ""

    assert get(transport, "/a") == ""
    assert calls == ["/a"]


def test_get_retries_until_transport_succeeds():
    """None signals failure; the next attempt's result is returned."""
    responses = iter([None, None, "ok"])

    assert get(lambda path: next(responses), "/a") == "ok"


def test_get_gives_up_after_max_attempts():
    """Persistent failure stops after MAX_ATTEMPTS and returns an empty string."""
    calls = []

    def transport(path):
        calls.append(path)

    assert get(transport, "/a") == ""
    assert len(calls) == MAX_ATTEMPTS
```

**Why the first test is the regression test.** Against a truthiness check, the transport returns `""`, gets retried, and `calls` ends up as `["/a", "/a", "/a"]`. The return value is `""` either way, so the test has to assert on the call count to fail. The other two tests pin the retry contract and should pass both before and after the fix.

**Still to do:**
1. Save the file as `tests/test_client.py`.
2. Temporarily change line 10 to `if result:` and run `pytest tests/test_client.py`. `test_get_does_not_retry_an_empty_response` should fail and the other two should pass.
3. Restore the fix and run the full suite.
4. Run `ruff check`, `ruff format --check` and `ty check`. I didn't find a `pyproject.toml` or a `tox`/Makefile entry point, so I don't know how you run the suite here.

If you tell me what the bug was, or enable Write and Bash, I'll adjust the test and do the fail-then-pass check myself.
