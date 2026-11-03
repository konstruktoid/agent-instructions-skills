These are all **test doubles**: objects that stand in for a real dependency during a test. They differ in what they do and in what the test checks.

## Stub: returns canned answers
A stub gives fixed responses so the code under test can run. It has no logic of its own, and the test doesn't check how the stub was used. You check the **output** of the code under test.

```python
class StubRateService:
    def get_rate(self, currency):
        return 1.25  # always the same answer

def test_convert():
    assert convert(100, "EUR", rates=StubRateService()) == 125
```

## Mock: checks how it was called
A mock is set up with expectations about the calls it should get, and the test asserts on those calls. You check the **interaction**: was it called, with what arguments, and how many times.

```python
from unittest.mock import Mock

def test_signup_sends_welcome_email():
    mailer = Mock()
    signup("ada@example.com", mailer=mailer)
    mailer.send.assert_called_once_with("ada@example.com", subject="Welcome")
```

## Fake: a simpler working version
A fake has real working behavior but takes a shortcut that makes it unsuitable for production. Common examples are an in-memory database, a dict-backed cache or a fake filesystem. You check the **resulting state**.

```python
class FakeUserRepo:
    def __init__(self):
        self._users = {}
    def add(self, user):
        self._users[user.id] = user
    def get(self, user_id):
        return self._users.get(user_id)

def test_rename_user():
    repo = FakeUserRepo()
    repo.add(User(id=1, name="Ada"))
    rename_user(1, "Grace", repo=repo)
    assert repo.get(1).name == "Grace"
```

## Side by side

| | Stub | Mock | Fake |
|---|---|---|---|
| Has real logic? | No | No | Yes (simplified) |
| Main job | Supply inputs | Check calls | Stand in for the real thing |
| Test checks | Output | Interactions | Resulting state |
| Main risk | Too little realism | Tests tied to implementation details | Behaving differently from the real thing |

## Practical notes (Python)
- **`Mock` doesn't make something a mock.** `Mock(return_value=...)` that you never assert on is really a stub. What makes something a mock is asserting on its calls.
- **Use `autospec`.** `create_autospec(RealClass)` or `patch(..., autospec=True)` makes the double reject calls the real object wouldn't accept. Without it, a renamed method or a typo in an assertion can pass silently.
- **Use mocks sparingly.** Assert on calls only when the call *is* the behavior you care about, such as sending an email, charging a card or publishing an event. Otherwise, checking state with stubs or fakes makes tests less brittle when you refactor.
- **Check fakes against the real thing.** Run one set of contract tests against both the fake and the real implementation so they don't drift apart.

Related terms: a **dummy** is passed only to fill a parameter and is never used. A **spy** records its calls so you can check them afterward. In Python, `Mock` does this by default, and `wraps=` lets it record calls while still running the real object.
