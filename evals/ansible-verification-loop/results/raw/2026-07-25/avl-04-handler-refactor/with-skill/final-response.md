Everything checks out. Summary:

**Changes made** (`tasks/main.yml`, `handlers/main.yml`, `molecule/default/verify.yml`, `README.md`):
- Removed the two inline `ansible.builtin.service: state: restarted` tasks.
- Added a `Restart auditd` handler and had the config (`max_log_file`), new `num_logs`, and rules tasks all `notify` it.
- Added the missing `num_logs` task, applied the same way as `max_log_file` (previously documented but never written to `auditd.conf`).
- Updated `molecule/default/verify.yml` to slurp `auditd.conf` and assert both `max_log_file` and `num_logs` are set correctly.
- Updated the README line describing restart behavior.

**Verification performed:**
- `ansible-lint`: clean (production profile).
- `ansible-playbook --syntax-check`: passed.
- `molecule test`: not runnable — this fixture role has no `molecule/default/molecule.yml`, and that was true in the original baseline commit too, not something I removed. `uvx ... molecule test` failed immediately with `'molecule/default/molecule.yml' glob failed`.
- As a substitute, I ran the role directly against a live Debian container via `ansible-playbook` (docker connection), three times:
  1. First run: rules task changed, handler ran exactly once.
  2. Second run (no var changes): zero tasks changed, handler did **not** run — idempotence confirmed.
  3. Third run with different `auditd_max_log_file`/`auditd_num_logs` values: both config tasks changed simultaneously, but the handler still ran only **once** — confirming the restart-dedup behavior the task asked for. `auditd.conf` showed the correct applied values in each case.

One caveat to flag: since `molecule.yml` is missing from this scenario, the standard `molecule test` entry point can't actually be run here — I verified the equivalent behavior manually against a real container instead.
