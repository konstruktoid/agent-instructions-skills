# Injection and Untrusted Input

Read this when the change accepts external input, builds a query, renders output, calls
out to the shell, or evaluates code.

Ruff's `S` rules (ported from bandit) catch many of these patterns syntactically, but
cannot trace data flow across calls. Treat an `S`-rule pass as a floor, not proof.

## Input validation

- Validate all external input (user input, scraped data, upstream API responses) at the
  point it enters the system, not at every layer below it. Validate against a schema or an
  allowlist, and reject what does not match rather than editing it into shape: a sanitizer
  that rewrites input silently corrupts data that was merely unusual.
- Input validation is not a substitute for handling the value safely where it is used.
  Escaping for HTML, parameterizing SQL, passing argument lists to a subprocess, and
  normalizing what reaches a log are all decided at the sink, by its context, and each is
  still required after the input has been validated. OWASP treats these as two separate
  controls, and one ingress filter cannot stand in for all of them.
- Prefer allowlists over denylists, and enforce length limits.
- Watch for catastrophic-backtracking regular expressions (ReDoS) when validating
  untrusted input. Prefer simple patterns over nested quantifiers.

## SQL and query construction

- Use parameterized queries or an ORM (`sqlalchemy`, `psycopg2` placeholders).
- Never build queries with f-strings, `.format()`, or `%` on untrusted input. `S608`
  catches the obvious literal case, not input assembled several calls away.

## Templating and rendered output

- Use framework escaping (`markupsafe.escape`, `django.utils.html.escape`) or `bleach` for
  anything rendered as HTML. `flask.escape` was deprecated in Flask 2.3 and removed in 2.4;
  it was always the MarkupSafe function re-exported, so import it from `markupsafe`.
- Autoescaping in a template engine covers the template path only. Anything marked safe,
  or assembled as raw HTML in Python, is your responsibility.

## Command and code injection

- Avoid `eval` and `exec` on anything derived from user input (`S307`).
- Avoid `subprocess` with `shell=True` and `os.system` on strings built from untrusted
  input (`S602` to `S607`). Pass argument lists instead of shell strings.

## String formatting for security-sensitive output

- For text substitution driven by a caller-supplied format, prefer `string.Template` over
  f-strings and `.format()`. The risk it removes is a template string that is itself
  untrusted: `.format()` on such a string can reach attribute and item access, and so read
  object internals. An f-string evaluates expressions written in the source, not the values
  substituted into it, so an f-string over untrusted *values* is not an injection risk on
  its own.
- `string.Template` is not a security boundary for the substituted values. It restricts
  placeholder syntax and nothing else: it does not escape HTML, parameterize SQL, quote a
  shell argument, or neutralize a log record. Those remain the sink's job.
- Never concatenate untrusted input directly into a SQL string, a shell command, or a
  log format string.

## Log injection

- Treat any user-controlled string written to a log as a potential log-injection vector.
  Do not interpolate it unsanitized into a format string.
- For what must never reach a log at all, see [secrets.md](secrets.md).

## Related

Server-side requests to user-influenced destinations (SSRF) are covered in
[access-control.md](access-control.md), following OWASP's classification.
