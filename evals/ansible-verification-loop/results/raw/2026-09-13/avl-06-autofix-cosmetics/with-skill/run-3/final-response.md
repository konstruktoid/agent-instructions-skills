No molecule/tox/Makefile test setup exists — lint is the only verification gate present. Diff is minimal and scoped exactly to the requested changes, with no unrelated formatting churn.

Lint went from 4 failures (production profile failed) to a clean pass. Files changed: `tasks/main.yml` (task name casing, FQCN), `defaults/main.yml`, `templates/chrony.conf.j2`, `README.md` (new `ntp_client_min_sources` variable, default 2, rendered as `minsources`).

/clear before starting anything unrelated.
