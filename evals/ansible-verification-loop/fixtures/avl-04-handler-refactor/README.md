# auditd_rules

Installs auditd and applies a hardening rule set.

## Role variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `auditd_max_log_file` | `8` | Maximum audit log size in MiB. |
| `auditd_num_logs` | `5` | Number of rotated audit logs to keep. |
| `auditd_rules_path` | `/etc/audit/rules.d/hardening.rules` | Where the rule set is written. |

The role restarts auditd directly after each change.
