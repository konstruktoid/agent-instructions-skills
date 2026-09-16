Done. Summary:

- `defaults/main.yml`: added `certbot_staging: false`
- `tasks/main.yml`: the certificate-request command now appends `--staging` when `certbot_staging` is true, and the task is skipped via `when: certbot_valid_count.stdout | int == 0` (reusing the existing `certbot_valid_count` registered by the earlier `certbot certificates | grep -c "VALID"` task)
- `README.md`: documented the new variable

Verification performed:
- `ansible-lint .` before/after: identical 6 pre-existing findings (unnamed shell task, fqcn, no-changed-when ×2, risky-shell-pipe, risky-file-permissions) — no new findings introduced.
- `ansible-playbook --syntax-check` passes on a throwaway wrapper playbook.
- Rendered the exact command template and `when` expression through the real Jinja/Ansible engine for all four combinations of `certbot_staging` (true/false) × valid-count (0/1): `--staging` is appended only when true, and the task correctly runs only when the count is 0.
- Confirmed `certbot_staging: false` in `defaults/main.yml` loads as an actual boolean, not a string.

I did not attempt a full end-to-end role run, since that would require installing the `certbot` package (a privileged, state-changing operation) — flag if you want me to do that with your go-ahead. No `meta/argument_specs.yml` exists in this role, and there's no molecule/test scaffolding to update. No unrelated files changed.
