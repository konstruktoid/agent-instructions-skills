`ansible-lint` now passes cleanly on the `production` profile, with 0 failures and 0 warnings. The role has no molecule, tox or other tests, so lint was the only check I could run.

**Lint findings cleared.** There were four, all in `tasks/main.yml`:
- Two task names now start with a capital letter: "Render …" and "Manage …".
- `template` is now `ansible.builtin.template`, and `service` is now `ansible.builtin.service`.

I made these edits by hand rather than with `--fix`, so nothing else in the files was reformatted. The `git diff --stat` shows only the intended lines changed.

**New `ntp_client_min_sources` variable:**
- **Default:** `defaults/main.yml` sets it to `2`, with a comment in the file's existing style.
- **Template:** `templates/chrony.conf.j2` renders `minsources {{ ntp_client_min_sources }}` after the `makestep` line.
- **README:** the variable table has a new row for it.
- **Argument spec:** the role has no `meta/argument_specs.yml`, so there was nothing to update there.

I didn't create any new files, and the working tree shows only those four modified files.
