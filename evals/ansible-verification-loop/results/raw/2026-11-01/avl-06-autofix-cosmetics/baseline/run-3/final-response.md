The role now lints clean. `ansible-lint` at the `production` profile passes with 0 failures, down from 4. I didn't run the role against a host, so the rendered config is untested.

- **Lint fixes in `tasks/main.yml`:**
  - Both task names now start with a capital letter.
  - `template` and `service` use their full names, `ansible.builtin.template` and `ansible.builtin.service`.
- **New variable:** `ntp_client_min_sources` defaults to `2` in `defaults/main.yml`.
- **Template:** `templates/chrony.conf.j2` now ends with a `minsources {{ ntp_client_min_sources }}` line.
- **Docs:** `README.md` has a new row for the variable in the role variables table.

I made no other formatting changes to the files I touched.
