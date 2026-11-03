`ansible-lint` now passes on the production profile with 0 failures and 0 warnings. Before the change it reported 4 findings in `tasks/main.yml`.

- **Lint fixes:** I capitalised the two task names ("Render…", "Manage…"). I also switched `template` and `service` to `ansible.builtin.template` and `ansible.builtin.service`.
- **New variable:** `ntp_client_min_sources` defaults to `2` in `defaults/main.yml`. `templates/chrony.conf.j2` renders it as `minsources {{ ntp_client_min_sources }}`, and I added a row for it to the README variables table.

I didn't render the template or run the role, so I haven't checked how `chrony` handles the new `minsources` line. I left the formatting of the files I touched as it was.
