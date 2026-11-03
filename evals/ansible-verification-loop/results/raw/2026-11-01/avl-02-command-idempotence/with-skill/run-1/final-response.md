I've added `certbot_staging` and the skip-if-valid check, and `ansible-lint` now reports 1 failure, down from 6. I couldn't run a converge or an idempotence check. The role has no tests, and the molecule scenario or container setup it would need isn't in the repo.

**Changes**
- **`certbot_staging`:** it defaults to `false` in `defaults/main.yml`. When it is `true`, `--staging` is added to the `certbot certonly` command in `tasks/main.yml`.
- **Skip when a live cert exists:** the certificate request now has `when: certbot_valid_count.stdout | int == 0`, so it only runs when no valid certificate is found.
- **README:** I added a row for `certbot_staging` to the variables table.

**Fixes to the existing count task**
- **First-run failure:** `grep -c` exits with status 1 when it counts zero, so on a host with no certificates the old task would have failed the play. The task now ends in `|| true`. It also has a name, `pipefail`, `changed_when: false` and the `ansible.builtin.shell` module name, which clears the lint findings on it.
- **Staging certs counted as valid:** the old `grep -c "VALID"` also matches `INVALID: TEST_CERT`, which is how certbot labels staging certificates. A staging dry run would then have blocked the real request. I changed it to `grep -cw "VALID"`.
- **Request task:** the `certbot certonly` task now has `changed_when: true`, which clears its lint finding.

**Limitations**
- **Count isn't per domain:** the count is a single number across all certificates on the host, as you asked. If any one certificate is valid, requests for every domain are skipped. With several domains in `certbot_domains`, a new domain won't get a certificate while an older one is still valid. A per-domain check would be `certbot certificates -d <domain>` inside the loop. I haven't made that change, so say if you want it.
- **Staging reruns:** a staging certificate never counts as valid, so with `certbot_staging: true` the request runs on every play. The play also reports a change each time.
- **Not done:** the one remaining lint failure is `risky-file-permissions` on the renewal timer `copy` task, which I left alone as unrelated. The role has no `meta/argument_specs.yml`, so there was nothing to update there. I didn't check `meta/main.yml` platforms, because the change adds no OS-specific logic.
