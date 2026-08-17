# Access Control and SSRF

Read this when the change touches authorization, permissions, or a server-side request
to a destination the user can influence.

## Server-side authorization

- Enforce authorization server-side, through decorators or middleware (Flask-Security,
  Django Guardian, DRF permissions). Never rely on the client, or on the UI hiding
  something, as the only control.
- Check authorization against the object being acted on, not only the endpoint. An
  endpoint-level check that omits an ownership test is the standard insecure-direct-
  object-reference bug.
- Apply least privilege to database roles and file permissions. `S103` flags overly
  permissive `chmod` literals, not database grants.

## Server-side request forgery

Before making a server-side HTTP request to a URL or host derived from user input
(webhooks, callback URLs, "fetch this link" features):

- Validate the destination against an allowlist.
- Block requests to internal, link-local, and loopback address ranges.
- Resolve and check the address that will actually be connected to, and disable or bound
  redirect following, so a permitted hostname cannot redirect into the internal network.

No `S`-rule catches SSRF. OWASP folds it into Broken Access Control (A01:2025).

## Fail closed

A security check must fail closed. A broad `except:` or `except Exception:` around an
authorization or cryptographic check can silently turn a failure into an allow. `BLE`
and `TRY` keep handling narrow once a decision to handle something has been made, but do
not establish that this particular failure must deny.

This maps to OWASP's Mishandling of Exceptional Conditions category (A10:2025): a caught
exception that lets control flow continue past a failed check is as dangerous as an
uncaught one.

## Assertions

Never use a bare `assert` to enforce a security invariant (`S101` flags `assert` usage
in general). Assertions are stripped when Python runs with `-O`, so a security check must
never depend on them executing.

## Debug and error surfaces

- Ensure debug modes are off in production configuration (for example Django
  `DEBUG = False`).
- Ensure stack traces, environment details, and internal paths are never returned in
  responses. Confirm this post-deploy if the repository has a way to check.
- This is OWASP's Security Misconfiguration category (A02:2025).

## Concurrency

Watch for TOCTOU races on shared resources, for example temp file creation. `S108` flags
predictable temp paths, not the race itself. The same applies to deadlocks and race
conditions around anything guarding a security-relevant resource.
