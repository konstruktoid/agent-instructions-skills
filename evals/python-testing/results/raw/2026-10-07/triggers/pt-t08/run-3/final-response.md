These three are all "test doubles": stand-ins for a real dependency. They differ in what they do and in what you check with them.

## Stub
A stub returns canned answers so the code under test can run. You use it to control **inputs**.

```python
class StubClock:
    def now(self):
        return datetime(2026, 1, 1)
```

You assert on the result of the code under test. You don't assert on how the stub was called.

## Mock
A mock records how it was used, and the test asserts on those interactions. You use it to verify **outputs and side effects**, such as "was this called, and with what?"

```python
from unittest.mock import Mock

mailer = Mock()
register_user("a@b.com", mailer=mailer)
mailer.send.assert_called_once_with("a@b.com", subject="Welcome")
```

The test fails if the interaction is wrong, even when the return value is right.

## Fake
A fake is a **working, simplified implementation** with real behavior. It is usually too lightweight for production. Examples are an in-memory repository in place of a database, or a fake filesystem.

```python
class FakeUserRepo:
    def __init__(self):
        self._users = {}
    def add(self, user):
        self._users[user.id] = user
    def get(self, user_id):
        return self._users.get(user_id)
```

Because a fake keeps state and behaves consistently, tests can check outcomes: add a user, then get it back.

## Quick comparison

| | Behavior | Test asserts on | Typical use |
|---|---|---|---|
| **Stub** | Hardcoded responses | Code under test's result | Supply inputs, such as an API response or the time |
| **Mock** | Pre-programmed expectations, records calls | Interactions (calls and arguments) | Verify side effects, such as an email sent or an event published |
| **Fake** | Real, simplified logic | Final state or outcome | Replace heavy dependencies, such as a DB or queue |

## Practical notes
- **Terminology is loose.** In Python, `unittest.mock.Mock` and `MagicMock` can act as a stub (with `return_value=...`) or a mock (with `assert_called...`). The role depends on how you use it, not on the class.
- **Prefer fakes and stubs over mocks where practical.** Tests that assert on interactions are coupled to implementation details and break on refactors that don't change behavior.
- **Use mocks when the interaction is the behavior**, such as "a notification must be sent."
- A **spy** is a related double. It wraps the real thing and records calls.
