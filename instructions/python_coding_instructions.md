# Python Coding Instructions

## Objective

Produce Python code that passes the repository's `ruff` and `ty` checks
cleanly, plus the judgment calls those tools cannot make for you. These
instructions apply whenever an agent authors or modifies Python source in a
repository that adopts them.

For changes that touch input handling, deserialization, subprocess/OS calls,
SQL, templating, cryptography, secrets, or access control, also apply the
`python-secure-coding` skill (`skills/python/python-secure-coding/SKILL.md`),
which builds on this document's tooling baseline with Python-specific
security best practices that `ruff`/`ty` do not fully verify.

## Tooling

### Required

- Run commands through the repository's package manager (for example
  `uv run ruff check`, `uv run ty check`) rather than invoking `ruff`/`ty`
  directly, unless the repo has no such manager.
- Enable ruff's full rule set (`select = ["ALL"]` under `[tool.ruff.lint]`
  in `pyproject.toml`) rather than hand-picking a subset. Ignore individual
  rules only where they conflict with another enabled rule (for example
  `D203`/`D211`) or the project's formatter (`COM812`, `ISC001`), and record
  each ignore with a one-line reason next to it.
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

`ruff --select ALL` and `ty` catch syntax, style, import hygiene, unused
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
- **Security rationale.** For changes to authentication, authorization, or
  credential handling, state the security reasoning in the commit message
  or surrounding docstring. No check requires this, but it is expected.
- **Whether validation is needed at all.** `TRY`/`BLE` keep exception
  handling narrow once you have decided to handle something; they do not tell
  you that validation belongs only at genuine system boundaries (user
  input, network responses, external APIs) and not in between.
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
- The judgment items above (docstring/comment accuracy, secret flow,
  security rationale, boundary-only validation, batching) have been
  considered, since the tools cannot check them.
