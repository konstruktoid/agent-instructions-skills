Renders correctly, `minsources 2` present.

Changed: `tasks/main.yml` (task names capitalized, FQCN for `template`/`service`), `defaults/main.yml`, `templates/chrony.conf.j2`, `README.md` (new `ntp_client_min_sources` variable, default 2). `ansible-lint` now passes clean on the `production` profile (was 4 failures). Next: `/clear` before unrelated work.
