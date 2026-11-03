I moved the restarts into a handler and applied `auditd_num_logs`, but I couldn't run the molecule verification. The repo has no `molecule/default/molecule.yml`, so `molecule test` exits with "glob failed". `ansible-lint` passes with no failures.

- **Handler:** `handlers/main.yml` now defines `Restart auditd`. Both the configuration task and the rules task notify it, and the two direct restart tasks are gone. Ansible runs the handler once at the end of the play, and only if something changed. A second run with no changes should report no restart.
- **`auditd_num_logs`:** the log rotation task now loops over `max_log_file` and `num_logs`. It writes each to `auditd.conf` with `lineinfile`, the same way `max_log_file` was written before.
- **Verification:** `molecule/default/verify.yml` now reads `auditd.conf` and asserts that it contains `max_log_file = 8` and `num_logs = 5`. Those values are hardcoded in the verify play to match the role defaults, so they need updating if the defaults change.
- **README:** I replaced the line saying the role restarts auditd after each change with a description of the handler behavior.

I also haven't confirmed that the restarts really happen at most once, or that the rotation assertions pass against a real container.
