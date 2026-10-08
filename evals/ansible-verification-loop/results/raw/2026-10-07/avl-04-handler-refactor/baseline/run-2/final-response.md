I've made the changes, but I haven't run the role or the molecule scenario. `ansible-lint` passes and `verify.yml` passes `--syntax-check`.

I couldn't run molecule because the repo has no `molecule.yml`, so there's no driver or platform defined. I also didn't confirm that auditd restarts once and only on change.

- **Handler:** `handlers/main.yml` now defines `Restart auditd`. The two direct restart tasks are gone. The max-log-file, num-logs and rules tasks each notify the handler. Handlers are deduplicated, so auditd restarts once at the end of the play, and only if one of those tasks reported a change. A second run should report no changes.
- **`auditd_num_logs`:** A new `lineinfile` task sets `num_logs = {{ auditd_num_logs }}` in `auditd.conf`. It is written the same way as `max_log_file`, including mode `0640`.
- **Molecule verify:** `verify.yml` now reads `/etc/audit/auditd.conf` and asserts it has exactly one `max_log_file = <n>` line and one `num_logs = <n>` line. The expected values come from `auditd_max_log_file` and `auditd_num_logs`, falling back to the defaults of 8 and 5. Those variables only resolve if molecule passes the role's variables to the verify play. Otherwise the check uses the defaults.
- **README:** The last line now says auditd restarts at most once per run, through a handler.

To check idempotence, run a converge twice with a driver and confirm the second run reports `changed=0`.
