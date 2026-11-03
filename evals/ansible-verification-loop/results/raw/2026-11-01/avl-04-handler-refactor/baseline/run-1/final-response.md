I made the changes, but I couldn't run the Molecule scenario, so the handler behavior and the new verification have not been tested end to end.

`molecule test` fails because the repo has no `molecule/default/molecule.yml`. Only `ansible-lint` and `ansible-playbook --syntax-check` on `verify.yml` were run, and both passed.

- **`handlers/main.yml`:** There is now one `Restart auditd` handler. It was an empty `[]` before.
- **`tasks/main.yml`:** I removed both direct restart tasks. The rotation and rules tasks now notify the handler, so auditd restarts at most once, at the end of the play, and only if one of them changed something.
- **`auditd_num_logs`:** The rotation task now loops over two `lineinfile` entries, `max_log_file` and `num_logs`. Both are applied the same way, with the same path and mode.
- **`molecule/default/verify.yml`:** It now reads `auditd.conf`. It asserts that exactly one `max_log_file = 8` line and one `num_logs = 5` line are present, which are the role defaults.

Both new lines match against the default `auditd.conf` format (`key = value`). If a distro ships that file without the spaces around `=`, the `lineinfile` would append a duplicate line instead of replacing it. The verify assertion would catch that.

I haven't committed anything.
