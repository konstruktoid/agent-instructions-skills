Changes verified: `ansible-lint` output is unchanged aside from one line-number shift, `ansible-playbook --syntax-check` passes, and I confirmed by rendering the templated command that `certbot_staging: true` appends `--staging`, the default omits it, and the `when` condition correctly skips the request when `certbot_valid_count.stdout` is non-zero. No test/molecule setup or `meta/argument_specs.yml` exists in this role, so nothing else needed updating.

Files changed:
- `defaults/main.yml` — added `certbot_staging: false`
- `tasks/main.yml` — appends `--staging` when `certbot_staging` is true; added `when: certbot_valid_count.stdout | int == 0` to skip the request when a valid certificate already exists
- `README.md` — documented `certbot_staging`

/clear before starting anything unrelated.
