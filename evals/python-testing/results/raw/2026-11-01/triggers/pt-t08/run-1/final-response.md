These are all **test doubles**, objects that stand in for a real dependency during a test. They differ in what they're for and how you check them.

## Stub: returns canned answers
A stub has hardcoded responses so the code under test can run. It doesn't check how it was called. You still assert on the **output or state** of the code under test.

```python
class StubRates:
    def get_rate(self, currency):
        return 1.10  # always

def test_convert():
    assert convert(100, "EUR", rates=StubRates()) == 110.0
```

Use one when the dependency is just an **input** to your logic.

## Mock: records calls so you can check them
A mock is set up with expectations, or records its calls, and the test asserts on **how it was used**. This is behavior verification rather than state verification.

```python
from unittest.mock import Mock

def test_signup_sends_welcome_email():
    mailer = Mock()
    signup("a@example.com", mailer=mailer)
    mailer.send.assert_called_once_with("a@example.com", subject="Welcome")
```

Use one when the interaction **is** the result, for example sending an email, publishing an event, or writing an audit log.

Python's naming makes this confusing: `unittest.mock.Mock` can act as either. `Mock(return_value=...)` used only for its return value is a stub. It only becomes a mock in the strict sense when you call `assert_called_*` on it.

## Fake: a simpler version that really works
A fake actually works, but takes a shortcut that makes it unfit for production. Examples are an in-memory dict instead of a database, or a fake clock.

```python
class FakeUserRepo:
    def __init__(self):
        self._users = {}
    def save(self, user):
        self._users[user.id] = user
    def get(self, user_id):
        return self._users.get(user_id)
```

Use one when the code under test talks to the dependency in a stateful way, like save then load then update. A stub can't keep that state consistent, and mocks would make you script every call.

## Quick comparison

| | Has real logic? | What the test checks | Main risk |
|---|---|---|---|
| **Stub** | No, fixed answers | Output or state of the code under test | Fixed answers drift from real behavior |
| **Mock** | No | The calls made on the double | Tests break whenever the code is restructured, even if behavior is unchanged |
| **Fake** | Yes, simplified | Output or state | The fake's behavior drifts from the real thing (contract tests on both help) |

## In practice
- Prefer real objects when they're cheap and deterministic.
- Use a **fake** for stateful dependencies like repositories, caches or queues.
- Use a **stub** when you only need to control an input.
- Save **mocks** for checking calls that are the point of the code, especially at system boundaries like email, HTTP or message buses. Don't use them to check internal calls, or every refactor will break your tests.
- `mock.patch` with `autospec=True` (or `create_autospec`) makes the double reject calls the real interface wouldn't accept, so calls with wrong method names or arguments fail.

The names come from Gerard Meszaros's *xUnit Test Patterns*. The book also defines **dummies**, which are passed but never used, and **spies**, which are stubs that also record calls. Martin Fowler's essay "Mocks Aren't Stubs" is the classic write-up.
