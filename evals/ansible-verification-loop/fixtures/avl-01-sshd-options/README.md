# sshd_hardening

Applies a hardened sshd configuration.

## Role variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `sshd_port` | `22` | Port sshd listens on. |
| `sshd_permit_root_login` | `"no"` | Value for `PermitRootLogin`. |
| `sshd_password_authentication` | `"no"` | Value for `PasswordAuthentication`. |
| `sshd_config_path` | `/etc/ssh/sshd_config` | Path to the sshd configuration file. |

## Supported platforms

Debian bookworm.
