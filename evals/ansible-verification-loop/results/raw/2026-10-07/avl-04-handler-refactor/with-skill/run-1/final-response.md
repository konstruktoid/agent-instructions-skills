I've made the changes, but I couldn't run molecule, so the idempotence and restart behaviour is untested. The scenario has no `molecule.yml`, and `molecule test` stops with "glob failed". `ansible-lint` passes with 0 failures and 0 warnings, the same as before my edits. A syntax check on the role and on `verify.yml` also passes.

- **Handler:** `handlers/main.yml` now defines `Restart auditd`. The two direct restart tasks are gone. The rotation-limits task and the rules-copy task both notify the handler. auditd restarts at most once per run, and only if one of those tasks changed something.
- **`auditd_num_logs`:** the `auditd.conf` task now loops over `max_log_file` and `num_logs`, so both are applied with the same `lineinfile` pattern.
- **Verification:** `molecule/default/verify.yml` now reads `/etc/audit/auditd.conf` and asserts that exactly one `max_log_file = N` line and one `num_logs = N` line are present. The verify play can't see role defaults, so it falls back to the defaults (8 and 5) unless you pass `auditd_max_log_file` or `auditd_num_logs` into the verify play.
- **README:** it now says the restart goes through a handler.
- **Not touched:** the role has no `meta/argument_specs.yml`, so there was nothing to update there.

To check that a second converge reports no changes, the scenario needs a `molecule.yml` (a Docker driver would work, since Docker is available here). Then run `molecule test`.
