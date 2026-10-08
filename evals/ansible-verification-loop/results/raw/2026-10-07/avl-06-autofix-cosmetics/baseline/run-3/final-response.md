The role now lints clean: `ansible-lint` passes the production profile with 0 failures, and `yamllint` reports nothing. I didn't render the template or run the role.

- **Lint fixes in `tasks/main.yml`:** I capitalised the two task names ("Render…", "Manage…"). I also changed `template` and `service` to `ansible.builtin.template` and `ansible.builtin.service`. That was all four findings.
- **New variable:** `ntp_client_min_sources` defaults to `2` in `defaults/main.yml`. The template writes it as `minsources {{ ntp_client_min_sources }}`, just before the `driftfile` line. The README variable table has a new row for it.

I left the rest of the formatting in those files as it was.
