**Stub** — a fake object that returns canned/predetermined answers to calls made during the test. It has no logic beyond returning fixed values, and you don't verify calls made on it. Used to feed the code under test with the inputs it needs.

**Mock** — an object pre-programmed with expectations about which calls it should receive (arguments, order, count). The test asserts *on the mock itself* — "was this method called once, with these arguments?" It verifies interactions/behavior rather than state.

**Fake** — a working implementation, just not suitable for production (e.g., an in-memory database instead of a real one). It has real logic and can be used through multiple calls consistently, unlike a stub which just parrots fixed responses.

Quick rule of thumb:
- Stub → "give me this canned answer"
- Mock → "verify I was called correctly"
- Fake → "behave like the real thing, but lighter"

In Python, `unittest.mock.Mock`/`MagicMock` can act as either a stub (set `.return_value`) or a mock (assert with `.assert_called_with()`) depending on how you use it — the library doesn't force the distinction, but the terminology above still applies to how you're using the object in a given test.
