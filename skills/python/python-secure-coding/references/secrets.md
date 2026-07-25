# Secrets, Passwords, and Randomness

Read this when the change handles a credential, token, API key, password, or any
security-sensitive random value.

## Secret flow

`S105` to `S107` catch hardcoded-looking literals. They cannot trace a secret passed
through a variable into a log line, an error message, a generated file, or persisted
state. Trace that flow by hand.

- Load secrets from environment variables or a secrets manager. Never commit them to
  version control.
- Never let a secret reach logs, tracebacks, generated output, or client-visible
  responses.
- Check the repr of any object that holds a secret. A dataclass or a settings object
  prints its fields by default, and that repr ends up in exception output.

## Password and key handling

- Hash passwords with `bcrypt` or `Argon2`, with a per-user salt. Never MD5, SHA-1, or
  plain storage. `S303` and `S324` flag the weak-hash call, not the prior question of
  whether the value should be hashed at all.
- Use the `secrets` module, or `os.urandom`, for tokens, keys, and any
  security-sensitive randomness. Never `random` (`S311`).

## Constant-time comparison

Compare secrets, tokens, and MACs with `secrets.compare_digest()` or
`hmac.compare_digest()`, never `==`. The short-circuiting `==` comparison leaks the
length of the matching prefix through timing.

## Logging

Log security-relevant events (authentication failures, permission denials), but never
log secrets, tokens, or raw sensitive personal data. For log injection by
user-controlled strings, see [injection.md](injection.md).
