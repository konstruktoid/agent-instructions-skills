I moved the restarts into a handler and applied `auditd_num_logs`. I couldn't run the molecule scenario, so the changes are only lint-checked: `ansible-lint` passes, and it rates the role at the `production` profile.

- **Handler:** `handlers/main.yml` now defines a `Restart auditd` handler. The configuration and rules tasks both notify it, and the two direct restart tasks are gone. Ansible runs a notified handler once at the end of the play. So auditd restarts at most once per run, and not at all when nothing changed.
- **`auditd_num_logs`:** the configuration task now loops over `max_log_file` and `num_logs`, setting each line in `auditd.conf` the same way `max_log_file` was set before.
- **Verification:** `molecule/default/verify.yml` now reads `auditd.conf` and asserts that each setting appears exactly once with the expected value. The values come from the role defaults, 8 and 5, because the verify play doesn't load the role's defaults.
- **README:** the line saying the role restarts auditd directly now describes the handler.

**Not run:** the scenario has no `molecule.yml`, so `molecule test` has nothing to run. I haven't confirmed the idempotence or restart-once behaviour on a real host.

**Gap in verification:** the assertions check the rotation settings but not the restart count.
