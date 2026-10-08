The restarts now go through a single handler, and `auditd_num_logs` is applied to `auditd.conf`. I could not run molecule, so the converge, idempotence and verify steps are untested.

**What changed**
- **`handlers/main.yml`:** a new `Restart auditd` handler. It runs at most once at the end of the play, and only if something notified it.
- **`tasks/main.yml`:** the two direct restart tasks are gone. The `max_log_file` task, the new `num_logs` task and the rules task all notify the handler. The `num_logs` task is a `lineinfile` that mirrors the `max_log_file` one.
- **`README.md`:** the note about restarting after each change now describes the handler.
- **`molecule/default/verify.yml`:** it now reads `auditd.conf` and asserts that `max_log_file` and `num_logs` match the role variables, falling back to the defaults.

**Verification**
- **Lint:** `ansible-lint` passes with 0 failures and 0 warnings, the same result as before the change. The repo's lint config has no ignore list.
- **Syntax:** `ansible-playbook --syntax-check` passes with the role applied to localhost.
- **Molecule:** it can't run here. `molecule --version` crashes on an `ansible-config dump` error, and `molecule/default/` has no `molecule.yml`, so no driver or platform is defined. I did not invent one.
- **Not run:** the second-converge idempotence check, so "restarts only when something changed" is unconfirmed by a run.
- **Restart behaviour:** the handler logic is standard Ansible, but I did not run it.

**Left alone**
- There is no `meta/argument_specs.yml` in this role, so I did not add one.
- `meta/main.yml` platforms are unchanged, since nothing OS-specific changed.
