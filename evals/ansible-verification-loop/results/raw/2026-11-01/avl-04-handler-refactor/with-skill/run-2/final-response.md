I made the changes, but I couldn't run the molecule scenario, so the idempotence and restart behaviour is untested. `molecule test` fails immediately with `'molecule/default/molecule.yml' glob failed`, because the repo has no `molecule.yml`. I didn't add one. Every driver available here would write to `/etc/audit` on this machine or need a container runtime. The scenario needs a `molecule.yml` pointing at a Debian bookworm container before it can run.

What I did run: `ansible-lint` before and after (0 failures, 0 warnings both times, profile moderate), and `ansible-playbook --syntax-check` on `converge.yml` and `verify.yml`. Both pass.

- **Handler:** `handlers/main.yml` now defines `Restart auditd`. Handlers run once at the end of the play, so auditd restarts at most once per run and only if a task reported a change. The two direct restart tasks are gone from `tasks/main.yml`.
- **Notifications:** the rotation-limits task and the rules task both notify the handler.
- **`auditd_num_logs`:** the rotation-limits task now loops over `max_log_file` and `num_logs`. Both go into `auditd.conf` with the same `lineinfile` pattern as before.
- **README:** I replaced the line saying the role restarts auditd after each change with a description of the handler behaviour.
- **Verify:** `verify.yml` now reads `auditd.conf` and asserts that exactly one `max_log_file = …` line and one `num_logs = …` line match the expected values.
  - Those values are hardcoded fallbacks (8 and 5), because role defaults aren't visible to the verify play.
  - A non-default override in `converge.yml` would need the same values set in the verify play. I haven't added a non-default override.

The role has no `meta/argument_specs.yml` at all, so there was nothing to update there.

One caveat: `lineinfile` only replaces an existing `num_logs =` line. If a distro's `auditd.conf` doesn't have that line, the setting is appended rather than replaced.
