These are all "test doubles": stand-ins for a real dependency. They differ in what they do and what you check with them.

**Stub**
- It returns canned answers to calls, so the code under test can run.
- You don't assert on how it was called. It only supplies inputs.
- Example: a `get_exchange_rate()` that always returns `1.25`.

**Mock**
- It records how it was used, and you assert on those interactions. For example, you check that it was called once with certain arguments.
- Verifying behavior (the calls made) is its main job. It may also return canned values.
- Example: `mailer.send.assert_called_once_with("a@b.com", subject="Welcome")`.

**Fake**
- It's a real, working implementation that takes a shortcut and isn't suitable for production.
- It has real logic and state, so behavior carries across calls.
- Example: an in-memory repository backed by a dict instead of a database, or SQLite in place of Postgres.

**Quick comparison**

| | Returns canned data | Has real logic | You assert on calls |
|---|---|---|---|
| Stub | Yes | No | No |
| Mock | Optional | No | Yes |
| Fake | No (computes results) | Yes (simplified) | Usually no, you check resulting state |

**In Python**
- `unittest.mock.Mock` and `MagicMock` are general-purpose objects. Setting `return_value` makes one act as a stub. Calling `assert_called_*` makes it act as a mock. People often call everything a "mock" for this reason.
- A fake is usually a small hand-written class:

```python
class FakeUserRepo:
    def __init__(self):
        self._users = {}

    def add(self, user):
        self._users[user.id] = user

    def get(self, user_id):
        return self._users.get(user_id)
```

**When to use which**
- Use a **stub** when you only need to control what a dependency feeds into your code.
- Use a **mock** when the interaction is the outcome, such as "an email was sent" or "the API was called". Over-mocking couples tests to implementation details.
- Use a **fake** when the dependency is stateful and you want tests that stay realistic without the cost of the real thing. Fakes tend to survive refactors better than mocks.

Strictly speaking, the term "test double" covers all of these, plus *dummies* (placeholders that are passed but never used) and *spies* (wrappers that record calls on a real or stub object).
