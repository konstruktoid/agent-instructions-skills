# Cryptography and TLS

Read this when the change encrypts or signs data, configures TLS, or makes an outbound
connection whose certificate handling is in question.

## Use vetted libraries

- Use `cryptography` for encryption at rest. Do not hand-roll ciphers, modes, padding,
  or key derivation.
- Prefer a high-level recipe (for example Fernet) over assembling primitives, unless an
  interoperability requirement forces the lower-level API.

## TLS for data in transit

- Use TLS for anything crossing a network boundary, including internal service calls.
- Do not disable certificate verification (`S501`). `verify=False` in `requests`, or an
  unverified SSL context, defeats the protocol entirely and is not an acceptable fix for
  a certificate error. Fix the trust store or the certificate instead.
- Do not select known-weak protocols or ciphers (`S502` to `S509`). Take the library
  default unless there is a stated compatibility requirement, and record that
  requirement next to the setting.

## Key material

- Keys are secrets. Everything in [secrets.md](secrets.md) about storage, logging, and
  comparison applies to them.
- Plan for rotation. A key loaded once at import time from a constant path cannot be
  rotated without a restart, which is a decision worth stating rather than defaulting
  into.

## What the linter does not check

`S`-rules flag the weak call, not the design: whether the data needed encrypting, whether
the mode provides integrity as well as confidentiality, or whether a signature is
verified before its payload is used.
