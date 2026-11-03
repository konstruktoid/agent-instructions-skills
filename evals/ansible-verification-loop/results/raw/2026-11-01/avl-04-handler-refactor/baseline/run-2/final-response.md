I made the changes, but I couldn't run the molecule scenario, so the new verification hasn't been tested.

`molecule test` exits immediately because the repo has no `molecule/default/molecule.yml`. `ansible-lint` passes, and `converge.yml` and `verify.yml` pass `ansible-playbook --syntax-check`.

- **Handler:** `handlers/main.yml` now has a `Restart auditd` handler. The two direct restart tasks are gone. The auditd.conf task and the rules task both notify the handler, so auditd restarts at most once per run and only when one of them changed something.
- **`auditd_num_logs`:** the config task now loops over `max_log_file` and `num_logs`, so both are written to `auditd.conf` the same way.
- **Verification:** `molecule/default/verify.yml` now reads `/etc/audit/auditd.conf` and asserts that `max_log_file = …` and `num_logs = …` are present. It falls back to the role defaults of 8 and 5 because role variables aren't available in the verify play. If you override those variables in converge, the assertion has to use the same values.
- **README:** the last line now says the handler restarts auditd once, and only on change, instead of restarting after each change.

The verification doesn't check that the restart happens only once or only on change. Molecule's idempotence step would catch the "reports changed every time" part, but only once a `molecule.yml` exists.
