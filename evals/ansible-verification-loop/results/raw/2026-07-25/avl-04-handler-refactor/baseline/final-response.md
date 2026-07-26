Syntax checks pass. Summary of changes:

- **`tasks/main.yml`**: removed the two direct `service: restarted` tasks; each mutating task (`max_log_file`, new `num_logs`, hardening rules) now uses `notify: Restart auditd` instead.
- **`handlers/main.yml`**: added the `Restart auditd` handler, which only fires once, only when a notifying task actually changed something.
- **`defaults/main.yml`**: unchanged — `auditd_num_logs` already existed, just wasn't wired up.
- **`molecule/default/verify.yml`**: added assertions that `/etc/audit/auditd.conf` contains both `max_log_file = 8` and `num_logs = 5`.
- **`README.md`**: updated the note about restart behavior.
