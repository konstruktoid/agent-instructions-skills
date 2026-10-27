# Minimal Change Instructions

## Objective

Produce the smallest change that fully does what was asked, and say what it left out. These
instructions apply whenever an agent adds or modifies code, configuration, or tests in a repository
that adopts them, in any language. The language instructions state how to write the change. This
document states how much of it to write.

An agent that is not held to a size tends to overbuild: a helper the repository already has, a
dependency for a few lines, an option nobody requested. Each addition is code a reviewer must read
and a maintainer must keep. Size is not the goal on its own. A change that is short because it
dropped validation, error handling, or a requirement is not minimal, it is incomplete, and the
sections below say what may never be cut.

The reuse ladder and the shortcut comment adapt an idea from the ponytail project by DietrichGebert,
released under the MIT license. This document copies none of its text and depends on nothing from
it.

Measured effect: in `evals/minimal-change`, an agent following this document wrote less source than
one with no instruction and than one given the single sentence "Make the smallest complete change",
and it added tests. It used more output tokens than the sentence, and it did not change how the
agent reused existing helpers, handled errors, or covered a stated scope. Read the rules on reuse
and error handling as guidance that has not been shown to alter behavior. The first run with no
instruction had loaded the evaluating repository's own `AGENTS.md`; a repeat without it gave the
same result.

## The Reuse Ladder

### Required

- Read the code the change touches, trace its callers, and search the repository for an existing
  helper by name and by behavior, before choosing a rung. A rung picked without reading is a guess,
  and the usual result is a second implementation of something the repository already has.
- Climb the rungs in order and stop at the first one that fully works:
  1. Does it need to exist? A requirement that is already met, or a path no caller reaches, needs no
     new code. Never apply this rung to something the request asked for.
  2. Is it already in this codebase? Reuse the helper, constant, or pattern that is there, and
     extend it when it is nearly right.
  3. Does the standard library or the platform do it? Prefer the builtin, the shell parameter
     expansion, or the provider resource over new code.
  4. Does a dependency the repository already installs do it? Use it, unless the call costs more to
     read than the line it replaces.
  5. Can it be one readable line? Write the line.
  6. Otherwise write the minimum code that works, and no more.
- State the rung reached when it is not the sixth and the choice is not obvious, so a reviewer can
  check it.
- Change only what the request needs. A neighbouring cleanup belongs in its own change.

### Avoid

- A new helper, wrapper, or abstraction for a single call site.
- A configuration option, flag, or parameter nobody asked for.
- A new dependency for code that fits in a few lines. Adding one is a decision with a cost, covered
  under [Supply chain](#supply-chain), and the per-language rules against adding tools without
  checking for an existing equivalent apply to it as well.
- Reading rung 1 as permission to skip a requirement. See [Scope](#scope).

## What Is Never Cut

A smaller change never removes these. Each is part of doing the work, not an extra on top of it.

- Validation at a trust boundary: user input, requests and responses that cross a network, files
  from outside the repository, and the arguments of an interface that callers outside the repository
  use. Validation between functions that trust each other is extra, and the section "Beyond What the
  Tools Check" in `instructions/python_coding_instructions.md` states where that line falls.
- Error handling that prevents data loss or silent failure, such as a write that checks its result
  or a transaction that rolls back.
- Security controls and their rationale. The secure-coding skills and instructions own the detail:
  `skills/python/python-secure-coding/SKILL.md`, `skills/bash/bash-secure-scripting/SKILL.md`, and
  `skills/terraform/terraform-secure-iac/SKILL.md`.
- Accessibility in anything a person uses.
- Everything the request asked for, including what it asked for in passing.

## Scope

A requirement that defines scope is the scope. When a benchmark, a compliance standard, a policy, or
an explicit instruction names what must exist, such as a set of CIS controls or a stated list of
fields, every item on it is required, and rung 1 never removes one. The ladder applies to how an
item is implemented, not to whether it is implemented.

When the requested scope looks larger than the need, say so in the closing line and build what was
asked.

## Supply chain

Rung 4 does not apply when the installed dependency is the problem: it is unmaintained, has a known
vulnerability, is unpinned or unlocked, or would be used at a broader scope than it has today.
Report that case as a finding and use rung 3, 5, or 6 for the code at hand. A dependency problem
never justifies replacing a library for cryptography, parsing, or authentication with hand-written
code. Report it and keep the library until a vetted replacement exists.

A new dependency is a separate decision from rung 4, which only uses what is installed. Name the
dependency and the reason for it in the closing line when one is justified. The supply chain
references cover it:
`skills/python/python-secure-coding/references/supply-chain.md` for Python,
`skills/terraform/terraform-secure-iac/references/modules-supply-chain.md` for Terraform modules and
providers, and `skills/github/github-actions-security/references/supply-chain.md` for actions.

## Tests

- Where the language instructions, a testing skill, or the repository require a test for the
  change, including a regression test for a bug fix, that requirement applies. This document never
  lowers it.
- Beyond what is required, add one small test for new non-trivial logic: a branch, a loop, a
  parser, arithmetic on money, or anything that enforces security. One test that fails when the
  logic breaks is the target, not a matrix.
- Skip a test for configuration, a rename, or glue with no logic when nothing requires one, and say
  that none was added.
- Where the test goes, and how it matches the repository's layout, is covered by the testing
  skills: `skills/python/python-testing/SKILL.md`, `skills/bash/bash-testing/SKILL.md`, and
  `skills/terraform/terraform-testing/SKILL.md`.

## Marking a Shortcut

A shortcut is a deliberate choice of less than the general solution. Mark it with a comment on its
own line, in the language's comment syntax:

```text
shortcut: <the limit>, <when to upgrade>
```

For example, `shortcut: reads the whole file into memory, move to streaming above 100 MB`. A file
format with no comments carries the note in the closing line of the reply instead. A comment that
only says the code is simple, or that names no upgrade condition, is not a shortcut marker. Comment
length and placement follow the per-language instructions.

## Closing the Reply

End every reply that changes code with one or two lines stating what was skipped or not checked: a
cheaper option that was considered and did not fully work, the test that was not added and why, the
check that was not run, a requirement that looked larger than the need. A reply with nothing to
report says that. The line exists so a reviewer finds the omissions without reconstructing them
from the diff.

## Quality Checklist

Before considering a change complete, verify that:

- The code the change touches was read and its callers were traced, and the rung reached is not a
  guess.
- Nothing was added that the repository, the standard library, or an installed dependency already
  provides.
- No option, parameter, helper, or dependency was added that the request did not need.
- Every item a benchmark, standard, or explicit request required is present, and none was removed
  as unnecessary.
- Validation at trust boundaries, error handling that prevents data loss, security controls, and
  accessibility are intact.
- No dependency was newly used or added that is unmaintained, vulnerable, or unpinned, and a flawed
  dependency the code already used was reported.
- New non-trivial logic has one small test, or the reply says why it has none.
- Each deliberate shortcut carries a `shortcut:` comment naming its limit and its upgrade condition.
- The reply ends with what was skipped or not checked.
