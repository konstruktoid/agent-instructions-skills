---
name: python-testing
description: Adds or updates pytest coverage for a Python change by first discovering the repository's existing test layout and conventions, matching them rather than imposing a new structure, deciding whether the change requires a test at all, and running the suite in a bounded verify loop. Use when a Python change adds behavior, fixes a bug, changes a public interface, or touches security-relevant logic, and when deciding where a new test belongs in an unfamiliar repository.
capabilities:
  tools:
    - Bash
    - Edit
    - Glob
    - Grep
    - Read
    - Write
  shell:
    - pytest
    - ruff
    - tox
    - ty
    - uv
  paths:
    - "${CLAUDE_PLUGIN_ROOT}/instructions/"
    - "the target repository working tree"
  egress:
    - target-repository-tooling
---

# python-testing

## Purpose

Add pytest coverage that fits the repository it lands in. Most test damage comes from writing
tests before reading the ones already there: a second fixture style, a parallel directory layout,
or a mocking convention the project deliberately avoids. This skill orders the work as discover,
decide, write, verify.

## When to use this

- A Python change adds behavior, fixes a bug, or changes a public interface.
- A change touches security-relevant logic (input validation, authorization, crypto, secrets).
- Deciding where a test belongs in a repository whose layout is unfamiliar.

## When NOT to use this

- Non-Python changes.
- Repositories that use a test framework other than pytest. Follow what is there instead; do not
  introduce pytest alongside an existing framework.

## Steps

1. **Discover the existing layout before writing anything.** Do not assume a structure.
   - Find the test root: `tests/`, `test/`, alongside the source as `test_*.py`, or inside the
     package. Check `pyproject.toml`, `pytest.ini`, `setup.cfg`, and `tox.ini` for `testpaths`,
     `python_files`, `addopts`, and marker definitions.
   - Read two or three existing tests near the code being changed. Note the naming pattern, how
     fixtures are shared (`conftest.py`, factory functions, plain constructors), whether
     parametrization is used, and what the project mocks versus exercises for real.
   - Check for markers (`slow`, `integration`, `network`) and what the default run excludes.
2. **Decide whether a test is required.** See the table below. If a test is not required, say so
   and why, rather than silently skipping it.
3. **Write the test in the discovered style.** Match the existing naming, fixture, and assertion
   conventions. Do not introduce a new helper layer, a new mocking library, or a new directory
   when the repository already has an answer.
   - Assert on behavior and public interfaces, not on internal call sequences, unless the call
     itself is the contract.
   - For a bug fix, write the test so it fails against the unfixed code. Confirm that it does
     before applying the fix, or by reverting the fix once.
   - Keep each test independent: no shared mutable state, no ordering assumptions, no reliance on
     network or wall-clock time.
   - Keep the machine out of the test. A home-directory path, username, hostname, or real email
     address baked into a fixture, an expected value, or a recorded snapshot is both a test that
     only passes on one machine and information the repository has no reason to publish. Use
     `tmp_path`, `monkeypatch`, and placeholders, and normalize captured paths before asserting
     on them or committing a snapshot.
4. **Run the suite in the bounded verify loop below.**
5. Follow `instructions/python_coding_instructions.md` for the test code itself. Test files are
   source, and the same `ruff`/`ty` gate applies to them.

## When a test is required versus optional

| Change | Test |
|---|---|
| New function, class, or public interface | Required |
| Bug fix | Required, and it must fail without the fix |
| Changed behavior of existing code | Required, updating the existing test rather than adding a parallel one |
| Input validation, authorization, crypto, or secret handling | Required, including the rejection and failure paths |
| Refactor with no behavior change | Not required; existing tests must pass unchanged, and that is the evidence |
| Formatting, comments, docstrings, type annotations | Not required |
| Generated code or vendored dependencies | Not required unless the repository already tests them |

For anything else, ask what would have to break for the change to be wrong, and whether an
existing test would catch it.

## Verify

Run the repository's own entry point, not a bare `pytest` invocation, when one exists: a `tox`
env, a Makefile target, or the command in `.github/workflows/*.yml`. Through the package manager
where one is configured, for example `uv run pytest`.

- The full suite passes, not only the new tests.
- The new test fails against the unfixed or unchanged code, for a bug fix or a behavior change.
- Coverage tooling, if the repository has it configured, shows no drop. Do not add a coverage
  tool that is not already there.

### The bounded loop

One **attempt** is one full fix-and-rerun cycle: apply fixes for the failures from the previous
run, then rerun the suite to completion. Reading output, or re-reading a file without changing
anything, is not an attempt.

- Baseline the loop at 3 attempts.
- Continue past 3 only while making measurable progress, meaning each cycle ends with strictly
  fewer failures than the one before it.
- Stop early, before 3 attempts, if the loop is oscillating: the same failures recur, the count
  stops dropping, or a fix for one failure reintroduces another.
- When stopping for either reason, report to the user rather than proceeding or silently giving
  up. Name the failing test, include its output, and state what was tried.

Never weaken a test, mark it `xfail`, or skip it to get a green run. If a test is wrong, fix the
test and say why it was wrong.

## Verification checklist

- [ ] Existing test layout and conventions read before writing, and matched
- [ ] No new test framework, directory, or mocking library introduced alongside an existing one
- [ ] Test required by the table above was written, or its absence explained
- [ ] For a bug fix, the test was confirmed to fail without the fix
- [ ] Full suite run through the repository's own entry point, to a clean result or to a stop
      under the loop rules above, with failures reported
- [ ] `ruff check`, `ruff format --check`, and `ty check` clean on the test files too
- [ ] No test weakened, skipped, or marked `xfail` to obtain a green run
- [ ] Tests are independent of ordering, network access, and wall-clock time
- [ ] No home-directory path, username, hostname, or real email address in test code, fixtures, or
      committed snapshots; anything machine-specific is generated or normalized

## References

Paths starting `instructions/` are relative to this library's root. When this skill is installed
as a Claude Code plugin, read them at `${CLAUDE_PLUGIN_ROOT}/instructions/`, which resolves to the
installed copy.

- `instructions/python_coding_instructions.md`: the `ruff`/`ty` baseline, which applies to test
  code as well.
- `skills/python/python-secure-coding/SKILL.md`: for security-relevant changes, whose rejection
  and failure paths need coverage.
