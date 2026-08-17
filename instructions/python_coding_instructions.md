# Python Coding Instructions

## Objective

Produce Python code that passes the repository's `ruff` and `ty` checks
cleanly, and apply the judgment those tools cannot supply. These
instructions apply whenever an agent authors or modifies Python source in a
repository that adopts them.

Two skills build on this document and are worth applying alongside it:

- For changes that touch input handling, deserialization, subprocess/OS
  calls, SQL, templating, cryptography, secrets, or access control, apply
  the `python-secure-coding` skill
  (`skills/python/python-secure-coding/SKILL.md`), which extends this
  document's tooling baseline with Python-specific security practices that
  `ruff`/`ty` do not fully verify.
- For adding or updating test coverage, apply the `python-testing` skill
  (`skills/python/python-testing/SKILL.md`), which covers discovering the
  repository's existing test layout, deciding when a test is required, and
  running the suite in a bounded verify loop. Test files are source, so the
  tooling baseline below applies to them as well.

## Tooling

### Required

- Run commands through the repository's package manager (for example
  `uv run ruff check`, `uv run ty check`) rather than invoking `ruff`/`ty`
  directly, unless the repo has no such manager.
- If the repository already has a ruff or other lint configuration, follow
  it and do not modify it. Propose `select = ["ALL"]` under
  `[tool.ruff.lint]` in `pyproject.toml` only for a new project, or when the
  user asks for stricter linting. Where a full rule set is in use, ignore
  individual rules only if they conflict with another enabled rule (for
  example `D203`/`D211`) or the project's formatter (`COM812`, `ISC001`),
  and record each ignore with a one-line reason next to it.
- Set `target-version` (ruff) and the repo's Python floor (`ty`,
  `.python-version`, `requires-python`) so pyupgrade (`UP`) rules enforce
  syntax appropriate to that floor automatically. Do not hand-enforce syntax
  age.
- Run `ruff check`, `ruff format --check`, and `ty check` yourself before
  considering a change complete. Do not merely describe which commands
  should be run.

### Avoid

- Adding a new dependency, linter, or type checker without first checking
  whether the repository already has an equivalent configured.
- Weakening lint or type-check configuration to make a failing check pass.
  Fix the code instead, or add a narrowly scoped, justified ignore.
- Suppressing a finding (`# noqa`, `# type: ignore`, or equivalent) as a
  first response. Fix the underlying issue instead.

## Beyond What the Tools Check

A broad `ruff` rule set and `ty` catch syntax, style, import hygiene, unused
code, annotation presence, common bug patterns, and a wide swath of security
and correctness lint (`S`, `BLE`, `TRY`, `B`, `ASYNC`, `PERF`, and so on).
The following still require human judgment because no static check can
verify them:

- **Docstring and comment accuracy.** `D` rules require a docstring to
  exist; they cannot verify it is true or that a remaining comment explains
  a non-obvious "why" rather than restating the code.
- **Domain naming consistency.** `N` rules enforce case conventions, not
  whether a new name is a synonym for a concept the repo already names
  differently.
- **Secret flow through variables.** `S105`–`S107` catch hardcoded-looking
  literals; they cannot trace a credential passed through a variable into a
  log line, generated output, or persisted state.
- **User and system information in committed files.** No rule flags a home
  directory path, username, uid, hostname, internal IP, or real email address
  that reached source, a test fixture or snapshot, captured tool output, or
  generated documentation. These identify the machine a change was made on
  rather than anything about the code, and they make the file non-portable as
  well as over-shared. Use placeholders (`/path/to/project`,
  `user@example.com`, RFC 5737 addresses), derive real values at runtime from
  `Path.home()`, `getpass.getuser()`, or `socket.gethostname()`, and normalize
  captured output before writing it anywhere that gets committed.
- **Security rationale.** For changes to authentication, authorization, or
  credential handling, state the security reasoning in the commit message
  or surrounding docstring. No check requires this, but it is expected.
- **Whether validation is needed at all.** `TRY`/`BLE` keep exception
  handling narrow once a decision to handle something has been made; they do
  not establish that validation belongs only at genuine system boundaries
  (user input, network responses, external APIs) and not in between.
- **Missed batching opportunities.** No lint rule flags an external API
  call made in a loop that the API could batch.
- **Suppression justification.** A blanket `# noqa` is itself catchable
  (`PGH004`), but the quality of the one-line reason next to a scoped
  suppression is not. Never disable a rule repository-wide to silence one
  instance.

## Quality Checklist

Before considering a Python change complete, verify that:

- `ruff check .` passes with no new ignores.
- `ruff format --check .` passes.
- `ty check` passes with no new suppressions.
- Every ignore or suppression that remains, in config or inline, carries
  a one-line justification.
- The judgment items above (docstring/comment accuracy, secret flow, user and
  system information, security rationale, boundary-only validation, batching)
  have been considered, since the tools cannot check them.
- Nothing being committed carries a home-directory path, username, uid,
  hostname, internal IP, or real email address, including in test fixtures,
  captured output, and generated documentation.
- Test coverage was added or updated if the change adds behavior, fixes a
  bug, or changes a public interface, following the `python-testing` skill.
  If no test was added, the reason was stated rather than left implicit.
- The checks above were run, not merely described, and their output was
  seen. A change is not complete because the edit looks right.
