These three terms are "test doubles", which are stand-ins for real dependencies in tests. They differ in what they're for.

**Stub**
- Returns canned answers to calls. It has no logic of its own.
- You use it to control the *inputs* to the code under test.
- You don't assert on how it was called.
- Example: `get_exchange_rate()` always returns `1.25`.

**Fake**
- A working but simplified implementation.
- It has real behavior, but it takes shortcuts that make it unsuitable for production.
- Examples: an in-memory repository backed by a dict, a fake SMTP server that stores messages in a list, SQLite in place of Postgres.
- You use it when the code needs realistic, stateful behavior and the real thing is too slow or heavy.

**Mock**
- Records how it was called, and you assert on those calls.
- You use it to verify *outputs* or *interactions*: that the code called `send_email` once, with these arguments.
- It can also return canned values, but verifying the calls is what defines it.

**Quick comparison**

| | Returns canned data | Has working logic | Verifies calls |
|---|---|---|---|
| Stub | Yes | No | No |
| Fake | No (computes) | Yes (simplified) | No |
| Mock | Optional | No | Yes |

**Python example**

```python
from unittest.mock import Mock

# Stub: fixed response
rates = Mock()
rates.get.return_value = 1.25

# Fake: real, simplified behavior
class FakeUserRepo:
    def __init__(self):
        self._users = {}
    def save(self, user):
        self._users[user.id] = user
    def get(self, user_id):
        return self._users[user_id]

# Mock: assert on the interaction
mailer = Mock()
notify(user, mailer)
mailer.send.assert_called_once_with(user.email, "Welcome")
```

**Caveats**
- In Python, `unittest.mock.Mock` is used to build both stubs and mocks. What matters is how you use it. If you only set `return_value`, it's a stub. If you call `assert_called_*`, it's a mock.
- Many people say "mock" for all three. The distinctions come from Gerard Meszaros's *xUnit Test Patterns* and Martin Fowler's "Mocks Aren't Stubs".
- Fakes tend to make more durable tests. Mocks tie tests to implementation details, so they break more often on refactors.
