`ansible-lint` now passes on the `production` profile. I added `ntp_client_min_sources` as asked. Lint is the only check I ran. I didn't render the template or run the role against a host.

**Lint fixes** (all four findings were in `tasks/main.yml`):
- Both task names now start with an uppercase letter ("Render…" and "Manage…").
- `template` and `service` now use their full names, `ansible.builtin.template` and `ansible.builtin.service`.

**New variable:**
- `defaults/main.yml` sets `ntp_client_min_sources: 2`, with a comment.
- `templates/chrony.conf.j2` ends with `minsources {{ ntp_client_min_sources }}`.
- `README.md` has a new row for it in the variables table.

I changed nothing else in the files I touched, so existing formatting is as it was.
