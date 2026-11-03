I added `certbot_staging` (default `false`) and the skip for domains that already have a valid certificate. Lint and a syntax check pass for the changes, but I couldn't run the role against a real host. The role has no molecule or tox tests, so the idempotence check and a full test run never happened.

**What changed**
- **Staging flag:** `defaults/main.yml` has `certbot_staging: false`. When it is true, `tasks/main.yml` adds `--staging` to the `certbot certonly` command.
- **Per-domain count:** The old count task ran once for the whole host, so a single valid certificate would have skipped every domain. I changed it to count VALID lines per domain with `certbot certificates -d <domain>`. The request task runs only for domains whose count is 0.
- **Lint fixes on the count task:** While rewriting it, I gave it a name, `ansible.builtin.shell`, `pipefail`, `changed_when: false`, `check_mode: false`, and `failed_when` set so `grep -c` returning 1 (no match) isn't an error.
- **Request task:** Since it now only runs when a request is needed, I set `changed_when: true` on it.
- **README:** Added a `certbot_staging` row, and noted on `certbot_domains` that domains with a valid certificate are skipped.

**Verification**
- `ansible-lint` went from 6 failures to 1.
- The one left is `risky-file-permissions` on the "Write the renewal timer" task. It was already there, and I didn't touch that task.
- `ansible-playbook --syntax-check` passes.
- The role has no `meta/argument_specs.yml`, so there was nothing to update there.
- Only `README.md`, `defaults/main.yml` and `tasks/main.yml` changed, and nothing untracked was left behind.

The `--staging` flag and the skip logic have never run, so please try them on a host.
