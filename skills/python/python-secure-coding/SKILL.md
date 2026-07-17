---
name: python-secure-coding
description: Use this skill when authoring or modifying Python source code. Builds on the ruff/ty quality gate and adds Python-specific security best practices (input handling, deserialization, secrets, subprocess/SQL/crypto usage, dependency hygiene) that static analysis alone does not fully cover.
---

# python-secure-coding

## Purpose
Produce Python code that passes the repository's `ruff` and `ty` checks cleanly, and that
additionally follows Python security best practices no linter fully verifies on its own. This
skill extends the baseline ruff/ty workflow with a security layer drawn from OWASP/OSSF-aligned
guidance (see References). Use it for any Python authoring or modification, and apply extra
scrutiny when the change touches input handling, deserialization, subprocess/OS calls, SQL,
templating, crypto, secrets, or auth.

## When to use this
- Authoring or modifying Python source in a repository that adopts these instructions.
- Any change that touches user input, deserialization, subprocess/OS/shell calls, SQL or other
  query construction, templating, cryptography, passwords, secrets/credentials, or access control.

## When NOT to use this
- Non-Python changes.

## Tooling baseline (ruff + ty)
1. Run commands through the repository's package manager (for example `uv run ruff check`,
   `uv run ty check`) rather than invoking `ruff`/`ty` directly, unless the repo has no such
   manager.
2. Enable ruff's full rule set (`select = ["ALL"]` under `[tool.ruff.lint]` in `pyproject.toml`)
   rather than hand-picking a subset. This is what pulls in `S` (flake8-bandit), `BLE`, `TRY`,
   `ASYNC`, `PERF`, and other security-relevant lint families. Ignore individual rules only where
   they conflict with another enabled rule (e.g. `D203`/`D211`) or the project's formatter
   (`COM812`, `ISC001`), and record each ignore with a one-line reason next to it. Never disable
   an `S` (bandit) rule repository-wide to silence one instance. Suppress narrowly at the call
   site with a justification instead (see Step 3 below).
3. Set `target-version` (ruff) and the repo's Python floor (`ty`, `.python-version`,
   `requires-python`) so pyupgrade (`UP`) rules enforce syntax appropriate to that floor
   automatically.
4. Run `ruff check`, `ruff format --check`, and `ty check` yourself before considering a change
   complete. Do not merely describe which commands should be run.
5. Do not add a new dependency, linter, or type checker without first checking whether the
   repository already has an equivalent configured.
6. Do not weaken lint or type-check configuration, or suppress a finding (`# noqa`,
   `# type: ignore`, or equivalent) as a first response to make a failing check pass. Fix the
   underlying code instead.

## Security checklist beyond static analysis
Ruff's `S` rules (ported from bandit) catch many of these patterns syntactically, but cannot
trace data flow, judge trust boundaries, or check runtime configuration. Treat an `S`-rule pass
as a floor, not proof of security. Work through each category that is relevant to the change:

- **Input validation and injection.** Validate and sanitize all external input (user input,
  scraped data, upstream API responses) at the point it enters the system. Use parameterized
  queries or an ORM (`sqlalchemy`, `psycopg2` placeholders) for SQL. Never build queries via
  f-strings or `.format()`/`%` on untrusted input (`S608` catches the obvious literal case, not
  input assembled several calls away). Use framework escaping (`flask.escape`,
  `django.utils.html.escape`) or `bleach` for anything rendered as HTML.
- **Command/code injection.** Avoid `eval`/`exec` on anything derived from user input (`S307`).
  Avoid `subprocess` with `shell=True` or `os.system` on strings built from untrusted input
  (`S602`–`S607`); pass argument lists instead of shell strings.
- **String formatting for security-sensitive output.** For user-facing text substitution that
  must not evaluate expressions, prefer `string.Template` over f-strings/`.format()`. Never
  concatenate untrusted input directly into a SQL string, shell command, or log format string.
- **Deserialization.** Never unpickle (`pickle`, `marshal`, `shelve`) data from an untrusted or
  network source (`S301`). Use `yaml.safe_load` / `Loader=yaml.SafeLoader`, never
  `yaml.load`/`yaml.Loader` on untrusted YAML (`S506`). Use `defusedxml` instead of the stdlib
  `xml` modules when parsing untrusted XML, to avoid entity-expansion/XXE attacks.
- **Secrets and credentials.** `S105`–`S107` catch hardcoded-looking literals but not a secret
  passed through a variable into a log line, error message, generated file, or persisted state.
  Trace that flow by hand. Load secrets from environment variables or a secrets manager, never
  commit them to version control, and never let them reach logs, tracebacks, or client-visible
  responses.
- **Password and key handling.** Hash passwords with `bcrypt` or `Argon2` (with a per-user salt),
  never MD5/SHA-1/plain storage (`S303`/`S324` flag the weak-hash call but not "should this be
  hashed at all"). Use the `secrets` module (or `os.urandom`) for tokens, keys, and any
  security-sensitive randomness. Never use `random` (`S311`).
- **Cryptography and TLS.** Use vetted libraries (`cryptography`, not hand-rolled ciphers) for
  encryption at rest, and TLS for data in transit. Do not disable certificate verification
  (`S501`) or select known-weak protocols/ciphers (`S502`–`S509`).
- **Access control.** Enforce authorization server-side (decorators/middleware, e.g.
  Flask-Security, Django Guardian, DRF permissions), never rely on the client or UI hiding
  something as the only control. Apply least privilege to database roles and file permissions
  (`S103` flags overly permissive `chmod` literals, not database grants).
- **Debug and error surfaces.** Ensure debug modes are off in production config (e.g. Django
  `DEBUG = False`) and that stack traces, environment details, or internal paths are never
  returned in responses. Confirm this post-deploy if the repo has a way to check.
- **Logging.** Log security-relevant events (auth failures, permission denials) but never log
  secrets, tokens, or raw sensitive PII. Treat any user-controlled string written to a log as a
  potential log-injection vector. Do not interpolate it unsanitized into a format string.
- **Exception handling.** Catch specific exception types; a broad `except:`/`except Exception:`
  around an auth or crypto check can silently turn a failure into an allow (`BLE`/`TRY` keep
  handling narrow once you have decided to handle something, but do not tell you that a security
  check must fail closed).
- **Concurrency.** Watch for TOCTOU races on shared resources (e.g. temp file creation, `S108`
  flags predictable temp paths, not the race itself) and for deadlocks/race conditions around
  anything guarding a security-relevant resource.
- **Assertions.** Never use a bare `assert` to enforce a security invariant (`S101` flags
  `assert` usage in general). Assertions are stripped when Python runs with `-O`, so a
  security check must never depend on them executing.
- **Dependency hygiene.** Pin dependencies via a lockfile, check new packages for typosquatting
  before adding them, and run a dependency vulnerability scan (`pip-audit`, `uv pip audit`,
  Snyk, or whatever the repo already uses) rather than adding a new scanner. Use an isolated
  virtual environment rather than system Python.

## Judgment items no tool checks
- **Docstring and comment accuracy.** `D` rules require a docstring to exist, not that it (or a
  remaining comment) is true.
- **Domain naming consistency.** `N` rules enforce case conventions, not whether a new name
  duplicates a concept the repo already names differently.
- **Security rationale.** For changes to authentication, authorization, or credential handling,
  state the security reasoning in the commit message or surrounding docstring.
- **Whether validation is needed at all.** `TRY`/`BLE` do not tell you validation belongs only at
  genuine system boundaries (user input, network responses, external APIs), not in between.
- **Missed batching opportunities.** No lint rule flags an external API call made in a loop that
  the API could batch.
- **Suppression justification.** A blanket `# noqa` is itself catchable (`PGH004`), but the
  quality of the one-line reason next to a scoped suppression is not.

## Verify
- `ruff check .` passes with no new ignores.
- `ruff format --check .` passes.
- `ty check` passes with no new suppressions.
- Every ignore or suppression that remains, in config or inline, especially any `S`-rule
  suppression, carries a one-line justification.
- If a dependency scanner is already configured in the repo (`pip-audit`, Snyk, etc.), run it
  and confirm no new vulnerable dependency was introduced.
- Walk the "Security checklist beyond static analysis" categories relevant to the change and
  confirm each has been considered, not just the ones a linter would flag.

## Verification checklist
- [ ] `ruff check .` clean
- [ ] `ruff format --check .` clean
- [ ] `ty check` clean
- [ ] No new/weakened lint or type-check suppressions without a one-line justification
- [ ] Untrusted input (user input, network/API responses, files) is validated/sanitized at the
      boundary, not assumed safe downstream
- [ ] No untrusted data reaches `eval`/`exec`, `subprocess`/`os.system` with `shell=True`,
      `pickle`/`yaml.load`, or string-built SQL
- [ ] Secrets/credentials traced end-to-end: not hardcoded, not logged, not in tracebacks or
      responses
- [ ] Passwords hashed with bcrypt/Argon2; security-sensitive randomness uses `secrets`, not
      `random`
- [ ] Authorization enforced server-side; debug mode off in production config
- [ ] Dependency changes checked against the repo's existing vulnerability scanner (if any)

## References
- RealPython, [Security Best Practices](https://realpython.com/ref/best-practices/security/)
- SimeonOnSecurity, [Python Security Best Practices: Protecting Your Code and Data](https://simeononsecurity.com/articles/python-security-best-practices-protecting-code-data/)
- Snyk, [Python Security Best Practices Cheat Sheet](https://snyk.io/blog/python-security-best-practices-cheat-sheet/)
- OpenSSF, [Secure Coding Guide for Python](https://github.com/ossf/wg-best-practices-os-developers/tree/main/docs/Secure-Coding-Guide-for-Python)
