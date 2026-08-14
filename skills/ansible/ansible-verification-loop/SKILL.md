---
name: ansible-verification-loop
description: Reviews and modifies Ansible roles, collections, playbooks, and tasks, verified through the target repository's own lint/test loop rather than declaring success from the edit alone. Use when reviewing or modifying any Ansible role, collection, playbook, or task.
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
7. Verify the change (see checklist below) in a bounded loop. One **attempt** is one full
   fix-and-rerun cycle: apply fixes for the findings from the previous run, then rerun the
   verification commands to completion. Reading output or re-reading a file without changing
   anything is not an attempt.
   - Baseline the loop at 3 attempts.
   - Continue past 3 only while making measurable progress, meaning each cycle ends with strictly
     fewer findings than the one before it.
   - Stop early, before 3 attempts, if the loop is oscillating: the same findings recur, the count
     stops dropping, or a fix for one finding reintroduces another.
   - When stopping for either reason, report to the user rather than proceeding or silently giving
     up. Name the failing check, include its output, and state what was tried.
8. Report any issues found during verification, with detailed reproduction steps and relevant
   logs/output. Ansible output is unusually rich in machine detail: play recaps and `--diff` output
   name the target host, gathered facts carry hostnames, interfaces and internal addresses, and
   failure messages quote absolute paths under the invoking user's home. Strip that before pasting
   output anywhere it will be stored, and never commit it into the repository. The same applies to
   anything checked in as a fixture: use `localhost`, `example.com`, or RFC 5737 addresses
   (`192.0.2.0/24`) in inventories, host vars, and templates rather than a real host.

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
  first what the wrapper would have done for you: install `requirements.yml`, and always run
  `ansible-lint` as its own separate step. Molecule's own `lint` subcommand was removed in Molecule
  6.x and has not returned, so no version of a direct `molecule test`/`molecule converge` invocation
  lints for you; skipping the separate `ansible-lint` run silently drops the primary quality gate.
- While iterating on a single role, use `molecule converge` / `molecule verify` (or the equivalent
  faster subcommands for whatever framework is in use) instead of the full test cycle to save
  time, but always finish with a full test run before declaring the change verified.

## Verification checklist

Never declare this done based on the edit alone. Confirm each of the following:

- [ ] Verify loop run to a clean result, or stopped under the rules in step 7 with unresolved
      issues reported, naming the failing check and its output
- [ ] Lint passes
- [ ] Full test suite passes
- [ ] Idempotence holds (no changes reported on a second converge/apply)
- [ ] Test fixtures (verify files, converge vars, integration targets) updated if behavior or
      variables changed
- [ ] Platform/version support declarations (`meta/main.yml`, `galaxy.yml`) still match any
      OS-conditional logic
- [ ] No user or system information committed: inventories, host vars, templates, and any captured
      lint or molecule output use placeholder hosts and addresses, with no real hostname, home
      directory path, username, or internal IP
- [ ] No unrelated files changed

## References

- [references/yaml-quoting.md](references/yaml-quoting.md): YAML 1.2.2 scalar resolution and
  quoting, including the "Norway problem". Read it when a change touches quoting in a YAML file,
  or when justifying why a value must stay quoted.
