The restarts are now one handler, and `auditd_num_logs` is applied. I couldn't run the molecule scenario, so none of this has been run against a host.

- **Handler:** the two inline restarts are gone. `handlers/main.yml` now has a single `Restart auditd` handler. The rotation task and the rules task both notify it, so auditd restarts at most once, at the end of the play, and only if one of them changed something.
- **`auditd_num_logs`:** the rotation task now loops over `max_log_file` and `num_logs`, and each is set with `lineinfile` as before.
- **Molecule verify:** `molecule/default/verify.yml` now reads `/etc/audit/auditd.conf` and asserts `max_log_file = 8` and `num_logs = 5`. Those match the defaults, so the assertions would fail if someone overrides the variables in converge.
- **README:** the closing sentence now says the restart happens once, and only on change.

**Verification:**
- `ansible-lint` passes with 0 failures and 0 warnings, the same as before my change. The repo's `.ansible-lint` only excludes `.git/`, so no findings are being hidden.
- `verify.yml` passes `ansible-playbook --syntax-check`.
- The repo has no `molecule/default/molecule.yml`, so `molecule list` fails with a glob error. That means converge, idempotence and verify never ran, and I haven't confirmed that a second run reports no change or that the restart happens only on change.

**Other:**
- There's no `meta/argument_specs.yml` in this role, so I didn't add one.
- I haven't committed anything.

If you add a `molecule.yml` (docker is installed here), I can run the full cycle.
