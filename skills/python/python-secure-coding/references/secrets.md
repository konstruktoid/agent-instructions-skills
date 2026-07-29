# Secrets, Passwords, and Randomness

Read this when the change handles a credential, token, API key, password, any
security-sensitive random value, or anything identifying the machine the code runs on.

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

## User and system information

A credential is not the only thing worth keeping out of a committed file. Anything
identifying the machine a run happened on, or the person at it, is environment rather
than evidence, and it has no place in anything the repository stores:

- Absolute paths under a home directory (`/home/<name>`, `/Users/<name>`,
  `C:\Users\<name>`), which name both the user and where they keep their work.
- Usernames, uids, gids, and the owner columns of captured `ls -l` output.
- Hostnames, FQDNs, MAC addresses, and internal IP addresses.
- Real email addresses, and paths naming unrelated checkouts on the same machine.

Where this reaches persisted state, not just logs:

- **Captured tool output.** A traceback, a subprocess capture, a lint report, or a
  recorded transcript carries the absolute path of whatever produced it. Anything
  written to a file that will be committed has to be normalized first.
- **Test fixtures and snapshots.** A snapshot recorded from a local run embeds that
  run's paths, and then only passes on that machine. See the `python-testing` skill.
- **Generated docs and examples.** Write `/path/to/project`, `user@example.com`, or an
  RFC 5737 address (`192.0.2.0/24`), never a real one copied from a terminal.
- **Config and cache files the program writes.** Store paths relative to a known root
  where the format allows it, rather than resolving to an absolute one.

Derive the substitutions from the environment (`Path.home()`, `getpass.getuser()`,
`socket.gethostname()`) rather than hardcoding one machine's values, so the scrubbing
works for every contributor. Where the distinction between two locations is the point
being recorded, map them to two different placeholders: collapsing "inside the project"
and "outside in the real home" to one token erases the fact worth keeping.

## Logging

Log security-relevant events (authentication failures, permission denials), but never
log secrets, tokens, raw sensitive personal data, or the identifying values listed
above. For log injection by user-controlled strings, see [injection.md](injection.md).
