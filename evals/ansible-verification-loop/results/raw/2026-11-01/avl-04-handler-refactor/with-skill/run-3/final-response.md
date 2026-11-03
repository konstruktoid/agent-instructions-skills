The restarts are now a single `Restart auditd` handler, and `auditd_num_logs` is applied. I couldn't run molecule, so the converge, verify and idempotence runs didn't happen.

**What changed**
- **Handler:** `handlers/main.yml` now defines `Restart auditd`. The two direct restart tasks are gone. The rotation-settings task and the rules task both notify the handler, so auditd restarts at most once per run and only if `auditd.conf` or the rules file changed.
- **`auditd_num_logs`:** the rotation task now loops over `max_log_file` and `num_logs`, so `num_logs` is written to `auditd.conf` the same way `max_log_file` is.
- **README:** I replaced the line saying the role restarts auditd after each change with a description of the handler.
- **Molecule:** `converge.yml` sets `auditd_max_log_file: 10` and `auditd_num_logs: 7`. `verify.yml` reads `auditd.conf` and asserts both lines. I set the values at play level because task-level `vars` triggered a `var-naming[no-role-prefix]` lint failure.

**What I verified**
- `ansible-lint` passes with no failures or warnings, the same as before the change.
- `ansible-playbook --syntax-check` passes on `converge.yml` and `verify.yml`.

**What I did not verify**
- **No molecule run:** the scenario has no `molecule.yml`, so `molecule list` fails with "glob failed" and nothing can converge. I didn't invent a driver config. Someone needs to add one, then run `molecule test` to confirm the new assertions pass and that a second converge reports no changes.
- **No `argument_specs.yml`:** the role has no `meta/argument_specs.yml`, so there was nothing to update there.
- **Restart behaviour:** the handler's once-only, only-on-change behaviour follows from how Ansible handlers work, but I haven't observed it on a host.
