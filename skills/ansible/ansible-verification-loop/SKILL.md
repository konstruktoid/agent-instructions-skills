---
name: ansible-verification-loop
description: Use this skill when reviewing or modifying an Ansible role or collection (playbooks, roles, tasks). Verifies changes through an actual lint/test loop rather than declaring success from the edit alone.
---

# ansible-verification-loop

## Purpose
Provide a structured approach for reviewing and modifying Ansible roles and collections. Ensures
changes are made consistently with the target repo's own conventions, verified through a real
lint/test loop, and reported clearly. It works across different repos' test setups (molecule,
ansible-test, tox, pytest-ansible, etc.) by discovering what is actually there rather than assuming
one project's layout.

## When to use this
- Reviewing or modifying any Ansible role, collection, playbook, or task.
- You need to ensure changes are consistent with existing conventions and actually verified before
  being reported done.

## When NOT to use this
- Changes that do not involve Ansible roles, collections, playbooks, or tasks.

## Steps
1. Orient in the target role/collection before changing anything:
   - Read the relevant role's `defaults/main.yml`, `tasks/main.yml`, `meta/main.yml`, and any
     `handlers/`, `vars/`, `templates/` it touches.
   - For collections, also check `galaxy.yml`, `meta/runtime.yml`, and `requirements.yml` for
     dependencies and supported Ansible/Python versions.
2. Discover and follow the repo's own authoritative rules. Check for (roughly in priority order):
   `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `CONTRIBUTING.md`,
   `CLAUDE.md`, `AGENTS.md`, or a `docs/` style guide. If none exist, infer conventions from
   surrounding code (FQCN vs short module names, quoting style, variable naming, indentation).
   Regardless of what a repo's docs say, treat SSH/sudo/PAM/audit/SELinux/AppArmor/firewall/
   mounts/sysctl/services/auth-adjacent tasks as high-sensitivity.
3. Follow the existing conventions and patterns already in the codebase: naming, file structure,
   style.
4. If OS-conditional logic changes, keep `meta/main.yml` `galaxy_info.platforms` (role) or the
   collection's declared platform support in sync with it.
5. If default values, argument specs, or variable names change, update all relevant documentation
   (README, role docs, `meta/argument_specs.yml`, etc).
6. Add or update test coverage for the change. Discover how this repo actually tests roles before
   assuming a layout. Common patterns, roughly in order of how likely you are to find them:
   - Molecule scenarios per role (`roles/<name>/molecule/<scenario>/`).
   - A shared/centralized molecule setup exercising multiple roles together (e.g. one
     `converge.yml` that includes several roles plus per-role `verify_<role>.yml` files included
     from a shared `verify.yml`). If you find this pattern, add/update the entries for the role
     you touched rather than creating a new scenario.
   - `ansible-test` (collections): unit tests under `tests/unit/`, integration targets under
     `tests/integration/targets/`.
   - Plain `tox` envs wrapping any of the above. Check `tox.ini` for the actual env names before
     assuming what `tox -e <name>` runs.
   Match whatever pattern the repo already uses; do not introduce a new test framework alongside an
   existing one.
7. Verify the change (see checklist below). If issues are found, fix them and re-verify. Repeat
   until all issues are resolved or verification has been attempted 3 times, whichever comes
   first. If issues remain unresolved after 3 attempts, stop and report to the user instead of
   proceeding or silently giving up.
8. Report any issues found during verification, with detailed reproduction steps and relevant
   logs/output.

## Verify
- Run `ansible-lint` (or the repo's configured linter/config, e.g. a non-default `.ansible-lint`
  path) and confirm a clean exit / expected output. This is the primary quality gate. Do not add
  suppressions to silence findings from new changes just to get a clean run.
- Run the repo's full test entry point and confirm success. This is usually a `tox` env (check
  `tox.ini` / `tox -av` for the right one, e.g. `tox -e docker`, `tox -e molecule`), a Makefile
  target, or a CI workflow file (`.github/workflows/*.yml`) that spells out the exact commands.
  It typically installs dependencies (`requirements.yml`/`galaxy.yml`), lints, then converges and
  verifies in containers/VMs across the platforms the role/collection claims to support, including
  an idempotence check.
- If invoking `molecule test` / `ansible-test` directly instead of through the repo's wrapper, do
  first what the wrapper would have done for you (install `requirements.yml`, run the linter).
  Direct invocation skips those steps.
- While iterating on a single role, use `molecule converge` / `molecule verify` (or the equivalent
  faster subcommands for whatever framework is in use) instead of the full test cycle to save
  time, but always finish with a full test run before declaring the change verified.

## Verification checklist
Never declare this done based on the edit alone. Confirm each of the following:
- [ ] Lint passes
- [ ] Full test suite passes
- [ ] Idempotence holds (no changes reported on a second converge/apply)
- [ ] Test fixtures (verify files, converge vars, integration targets) updated if behavior or
      variables changed
- [ ] Platform/version support declarations (`meta/main.yml`, `galaxy.yml`) still match any
      OS-conditional logic
- [ ] No unrelated files changed
