I made the changes, but I couldn't run molecule, so the handler behaviour and the new verify assertions have not been run against a host. `ansible-lint` passes with 0 failures and 0 warnings, same as before the change. A syntax check of `verify.yml` also passes.

**Why molecule didn't run:** `molecule/default/` has only `converge.yml` and `verify.yml`, with no `molecule.yml` (driver or platform config) and no `tox.ini` or Makefile. I didn't invent a scenario config. The idempotence check, the full test run and the "restarts at most once" behaviour are therefore unconfirmed.

**What changed:**
- **`handlers/main.yml`:** it was an empty list. It now has a `Restart auditd` handler.
- **`tasks/main.yml`:**
  - **Restarts:** both direct restart tasks are gone. The rotation task and the rules task each notify the handler. auditd restarts once at the end of the play, and only if something changed.
  - **`num_logs`:** the rotation task is now a loop over `max_log_file` and `num_logs`, so `auditd_num_logs` is applied the same way as `auditd_max_log_file`.
- **`README.md`:** the line saying the role restarts auditd directly now describes the handler behaviour.
- **`molecule/default/verify.yml`:** it now reads `auditd.conf` and asserts that `max_log_file` and `num_logs` are set to the expected values.

**Limits of the verify check:**
- The verify play doesn't load role defaults, so the assertions fall back to hardcoded `8` and `5` unless the variables are passed in. If the defaults change, update them there too.
- The existing rules-file check still hardcodes the default path.

There is no `meta/argument_specs.yml` in this role, so I didn't add one.
