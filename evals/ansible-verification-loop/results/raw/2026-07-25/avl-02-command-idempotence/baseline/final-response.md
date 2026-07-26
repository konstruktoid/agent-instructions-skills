Changes are done:

- **`defaults/main.yml`**: added `certbot_staging: false`.
- **`tasks/main.yml`**: the certificate request command appends `--staging` when `certbot_staging` is true, and the whole loop now has `when: certbot_valid_count.stdout | int == 0` so it's skipped once valid certificates already exist (reusing the existing `certbot_valid_count` fact).
- **`README.md`**: documented the new `certbot_staging` variable.

Pre-existing ansible-lint warnings (missing task name, pipefail, file perms on the timer) are unrelated to this change and were already present before my edits.
