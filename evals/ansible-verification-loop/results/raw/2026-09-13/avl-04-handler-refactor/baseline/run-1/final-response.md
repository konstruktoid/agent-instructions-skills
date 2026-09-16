**Files changed:** `tasks/main.yml`, `handlers/main.yml`, `molecule/default/verify.yml`, `README.md`.

- Removed the two inline `service: restarted` tasks; the config, num_logs, and rules tasks now `notify: Restart auditd`.
- Added the missing `num_logs` line to `auditd.conf`, applied the same way as `max_log_file`.
- Added a handler (`handlers/main.yml`) that restarts auditd once, on notify.
- `verify.yml` now reads `auditd.conf` and asserts both `max_log_file` and `num_logs` are set correctly.
- README line describing restart behavior updated.

**Verification:** `ansible-lint` passes at the `production` profile (stricter than the configured `moderate`). Ran a full `molecule test`/`converge`/`verify` cycle (docker driver) in the foreground: converge showed the handler firing exactly once, only after the task that actually changed something (rules copy); a second converge was fully idempotent (`changed=0`, handler not notified); `verify` confirmed `max_log_file = 8` and `num_logs = 5` in `auditd.conf`, and `auditd -f` foreground output showed `max_log_size_parser called with: 8` / `num_logs_parser called with: 5`, proving the values parse correctly. The auditd service itself fails to actually start under Docker (`Error sending status request (Operation not permitted)`) — a known audit-netlink/container kernel limitation, unrelated to this role. All scratch test scaffolding (a temporary `molecule.yml`, `prepare.yml`, role symlink — this fixture ships without them) was created for testing and removed afterward; `git status` shows only the four files above changed.
