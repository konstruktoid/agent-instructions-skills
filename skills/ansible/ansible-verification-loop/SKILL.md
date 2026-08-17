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
- A change must be consistent with existing conventions and actually verified before being
  reported done.

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
   style. When the change is to make one of those conventions consistent across many files, measure
   the current ratio first, report it, and let it decide the target rather than assuming which form
   was intended. See [references/style-sweeps.md](references/style-sweeps.md).
4. If OS-conditional logic changes, keep `meta/main.yml` `galaxy_info.platforms` (role) or the
   collection's declared platform support in sync with it.
5. If default values, argument specs, or variable names change, update every place that restates
   them: README, role docs, and `meta/argument_specs.yml`. Check the argument spec explicitly. A
   variable added to `defaults/main.yml` and documented in the README but absent from
   `meta/argument_specs.yml` is the omission that survives review, because nothing fails without
   it. Adding or quoting a description can push its line past the repo's line-length limit; fold it
   with `>-` rather than leaving it long or letting an existing suppression absorb it.
6. Add or update test coverage for the change. Discover how this repo actually tests roles before
   assuming a layout. Common patterns, roughly in order of how often they occur:
   - Molecule scenarios per role (`roles/<name>/molecule/<scenario>/`).
   - A shared/centralized molecule setup exercising multiple roles together (e.g. one
     `converge.yml` that includes several roles plus per-role `verify_<role>.yml` files included
     from a shared `verify.yml`). Where this pattern is present, add or update the entries for the
     role that changed rather than creating a new scenario.
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
   Machine identifiers are not the only exposure. Ansible output can also carry passwords, API
   tokens, private keys, vaulted or `no_log`-worthy variable values, and credential-bearing URLs:
   `--diff` on a templated secret prints both versions, a failed `uri` or `get_url` task echoes its
   headers, and a verbose module failure dumps the arguments it was called with. Redact those before
   the output is pasted, stored, uploaded as a CI artifact, or attached to an issue, not only before
   it is committed. When a task handles a secret, `no_log: true` is the fix, so that there is
   nothing to redact in the first place.

## Verify

- Run `ansible-lint` (or the repo's configured linter/config, e.g. a non-default `.ansible-lint`
  path) and confirm a clean exit / expected output. This is the primary quality gate. Do not add
  suppressions to silence findings from new changes just to get a clean run, and do not silently
  inherit an existing one: where the repo has a lint-ignore file or inline skips, a finding the
  change just introduced is downgraded to an ignored warning and the run still passes. Compare the
  linter's full output, or at minimum its warning count, from before and after the change.
- If any command was run with `--fix`, or any formatter was run at all, read its `git diff` before
  continuing. `ansible-lint --fix` round-trips the file through a YAML library and rewrites
  formatting no rule flagged, so a clean lint result before and after is not evidence that it
  changed nothing. Revert any hunk the change does not explain. Both this and the ignored-warning
  case are covered in [references/style-sweeps.md](references/style-sweeps.md).
- Run the repo's full test entry point and confirm success. This is usually a `tox` env (check
  `tox.ini` / `tox -av` for the right one, e.g. `tox -e docker`, `tox -e molecule`), a Makefile
  target, or a CI workflow file (`.github/workflows/*.yml`) that spells out the exact commands.
  It typically installs dependencies (`requirements.yml`/`galaxy.yml`), lints, then converges and
  verifies in containers/VMs across the platforms the role/collection claims to support, including
  an idempotence check.
- A full cycle can run for tens of minutes, long enough to outlive the process the agent starts it
  from. Detach it so the run does not depend on whatever is watching it, and poll for a sentinel
  file rather than for the watcher:

  ```sh
  setsid bash -c '<test entry point> > run.log 2>&1; echo $? > run.done' < /dev/null > /dev/null 2>&1 &
  ```

  The poller dying is not the run dying. When a watcher is killed, look for the still-running
  process and for the sentinel before relaunching anything. A blind relaunch spends the full cycle
  again and risks two runs racing on the same containers or VMs. This decides whether the loop's
  attempt budget is spent on real findings or on lost runs. Keep the log and sentinel out of the
  repository, and remember the log carries the machine detail described in step 8.
- If invoking `molecule test` / `ansible-test` directly instead of through the repo's wrapper,
  perform first what the wrapper would otherwise have performed: install `requirements.yml`, and
  always run `ansible-lint` as its own separate step. Molecule's own `lint` subcommand was removed
  in Molecule 6.x and has not returned, so no version of a direct `molecule test`/`molecule
  converge` invocation lints anything; skipping the separate `ansible-lint` run silently drops the
  primary quality gate.
- While iterating on a single role, use `molecule converge` / `molecule verify` (or the equivalent
  faster subcommands for whatever framework is in use) instead of the full test cycle to save
  time, but always finish with a full test run before declaring the change verified.

## Verification checklist

Never declare this done based on the edit alone. Confirm each of the following:

- [ ] Verify loop run to a clean result, or stopped under the rules in step 7 with unresolved
      issues reported, naming the failing check and its output
- [ ] Lint passes, and its full output is unchanged from before the change apart from findings the
      change deliberately resolved, including lines the repo's lint-ignore file downgrades
- [ ] Every hunk produced by an auto-fixer or formatter reviewed in `git diff` and either explained
      or reverted
- [ ] Full test suite passes
- [ ] Idempotence holds (no changes reported on a second converge/apply)
- [ ] Test fixtures (verify files, converge vars, integration targets) updated if behavior or
      variables changed
- [ ] `meta/argument_specs.yml`, the README, and the role docs all list any variable that was
      added, renamed, or had its default changed
- [ ] Platform/version support declarations (`meta/main.yml`, `galaxy.yml`) still match any
      OS-conditional logic
- [ ] No user or system information committed: inventories, host vars, templates, and any captured
      lint or molecule output use placeholder hosts and addresses, with no real hostname, home
      directory path, username, or internal IP
- [ ] No secrets in anything reported, stored, or uploaded: no passwords, API tokens, private
      keys, vault contents, or credential-bearing URLs in pasted output, CI artifacts, or issue
      attachments, and `no_log: true` set on any task that handles one
- [ ] No unrelated files changed

## References

- [references/yaml-quoting.md](references/yaml-quoting.md): YAML 1.2.2 scalar resolution and
  quoting, including the "Norway problem", auditing existing quoting, and where quoting a value
  breaks it. Read it when a change touches quoting in a YAML file, or when justifying why a value
  must stay quoted.
- [references/style-sweeps.md](references/style-sweeps.md): what an auto-fixer rewrites beyond the
  rules, how a lint-ignore file hides a new finding, and how to measure a convention before
  editing every file that uses it. Read it before running `--fix` or a formatter, and before any
  repository-wide consistency change.

The documentation this skill writes into the repository, meaning role README entries and
`meta/argument_specs.yml` descriptions, follows `instructions/written_language_instructions.md`.
A description states what the variable controls and what changes when it is set, with no claim
about how important or powerful the setting is. That path is relative to this library's root;
when the skill is installed as a Claude Code plugin, read it at `${CLAUDE_PLUGIN_ROOT}/instructions/`.
