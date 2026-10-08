I've made the changes, but I haven't run them against a real host. `ansible-lint` passes and `--syntax-check` is clean on `converge.yml` and `verify.yml`. The `molecule/default` scenario has no `molecule.yml`, so `molecule test` can't run. That means the restart-once and idempotence behaviour is untested.

- **Handler:** `handlers/main.yml` now defines `Restart auditd`. The two direct restart tasks in `tasks/main.yml` are gone.
- **Notifications:** the rotation-settings task and the rules task both notify the handler. auditd restarts at most once per run, and not at all when nothing changed.
- **`auditd_num_logs`:** the existing `lineinfile` task now loops over `max_log_file` and `num_logs`, so both are written to `auditd.conf` the same way.
- **Verification:** `molecule/default/verify.yml` now greps `auditd.conf` and asserts that both `max_log_file` and `num_logs` hold the expected values. The assert falls back to 8 and 5 when the variables aren't set, because the verify play doesn't see the role defaults. If you override the variables in converge, pass the same values to verify.
- **README:** I replaced the line about restarting directly after each change with a description of the handler.

To run it properly, add a `molecule.yml` (a Debian bookworm docker platform matching `meta/main.yml`). The second converge should then report `changed=0` and the handler shouldn't fire.
