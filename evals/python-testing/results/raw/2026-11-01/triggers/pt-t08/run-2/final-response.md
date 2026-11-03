All three are **test doubles**: objects you swap in for a real dependency during a test. The difference is in what each one does and what your test checks.

## Stub: returns canned answers
A stub gives back preset responses so the code under test can run. It has no real logic, and you don't make assertions about how it was called.

```python
class StubRateService:
    def get_rate(self, currency):
        return 1.25  # always the same answer

def test_convert():
    assert convert(100, "EUR", rates=StubRateService()) == 125
```
**Use it when** the dependency only supplies input and you only care about your code's output.

## Mock: records calls so you can check them
A mock is set up so you can later assert *how it was used*: which methods were called, with which arguments, and how many times. The test passes or fails on those interactions, not just on the return value.

```python
from unittest.mock import Mock

def test_signup_sends_welcome_email():
    mailer = Mock()
    signup("ana@example.com", mailer=mailer)
    mailer.send.assert_called_once_with("ana@example.com", subject="Welcome!")
```
**Use it when** the behavior you're testing is a side effect, like sending an email, publishing an event, or calling an API.

## Fake: a simple implementation that really works
A fake has real logic, but it takes a shortcut that makes it unsuitable for production. Typical examples are an in-memory database, a dict-backed cache or a fake filesystem.

```python
class FakeUserRepo:
    def __init__(self):
        self._users = {}
    def save(self, user):
        self._users[user.id] = user
    def get(self, user_id):
        return self._users.get(user_id)

def test_rename_user():
    repo = FakeUserRepo()
    repo.save(User(id=1, name="old"))
    rename_user(1, "new", repo=repo)
    assert repo.get(1).name == "new"
```
**Use it when** the code makes several stateful calls against the dependency (save, then read back, then update) and scripting each response with stubs would be awkward.

## Quick comparison

| | Has real logic? | What the test checks | Main risk |
|---|---|---|---|
| **Stub** | No, fixed responses | Output/state of the code under test | Responses that drift from real behavior |
| **Mock** | No, records calls | Interactions (calls, arguments, counts) | Brittle tests that break when you refactor |
| **Fake** | Yes, simplified | Output/state, across realistic sequences | The fake's behavior diverging from the real thing |

## Practical notes for Python
- The library doesn't decide which kind of double you have. `unittest.mock.Mock` / `MagicMock` can act as a stub (`m.get_rate.return_value = 1.25`) or as a mock (`m.send.assert_called_once_with(...)`). What counts is whether you assert on the return value or on the calls.
- Use `create_autospec(RealClass)` or `Mock(spec=RealClass)` so the double rejects methods and signatures the real class doesn't have. This catches a whole class of tests that pass while the real code would fail.
- Prefer fakes and stubs where you can. Mock-heavy tests tend to pin down *how* the code works rather than *what* it does, so they break during refactors even when behavior hasn't changed.
- Martin Fowler's "Mocks Aren't Stubs" and Gerard Meszaros's *xUnit Test Patterns* are the classic references. They also define **dummies** (passed in only to fill a parameter, never used) and **spies** (stubs that also record calls, which is close to how Python's `Mock` behaves).
