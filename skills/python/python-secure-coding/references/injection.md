# Injection and Untrusted Input

Read this when the change accepts external input, builds a query, renders output, calls
out to the shell, or evaluates code.

Ruff's `S` rules (ported from bandit) catch many of these patterns syntactically, but
cannot trace data flow across calls. Treat an `S`-rule pass as a floor, not proof.

## Input validation

- Validate and sanitize all external input (user input, scraped data, upstream API
  responses) at the point it enters the system, not at every layer below it.
- Prefer allowlists over denylists, and enforce length limits.
- Watch for catastrophic-backtracking regular expressions (ReDoS) when validating
  untrusted input. Prefer simple patterns over nested quantifiers.

## SQL and query construction

- Use parameterized queries or an ORM (`sqlalchemy`, `psycopg2` placeholders).
- Never build queries with f-strings, `.format()`, or `%` on untrusted input. `S608`
  catches the obvious literal case, not input assembled several calls away.

## Templating and rendered output

- Use framework escaping (`flask.escape`, `django.utils.html.escape`) or `bleach` for
  anything rendered as HTML.
- Autoescaping in a template engine covers the template path only. Anything marked safe,
  or assembled as raw HTML in Python, is your responsibility.

## Command and code injection

- Avoid `eval` and `exec` on anything derived from user input (`S307`).
- Avoid `subprocess` with `shell=True` and `os.system` on strings built from untrusted
  input (`S602` to `S607`). Pass argument lists instead of shell strings.

## String formatting for security-sensitive output

- For user-facing text substitution that must not evaluate expressions, prefer
  `string.Template` over f-strings and `.format()`.
- Never concatenate untrusted input directly into a SQL string, a shell command, or a
  log format string.

## Log injection

- Treat any user-controlled string written to a log as a potential log-injection vector.
  Do not interpolate it unsanitized into a format string.
- For what must never reach a log at all, see [secrets.md](secrets.md).

## Related

Server-side requests to user-influenced destinations (SSRF) are covered in
[access-control.md](access-control.md), following OWASP's classification.
