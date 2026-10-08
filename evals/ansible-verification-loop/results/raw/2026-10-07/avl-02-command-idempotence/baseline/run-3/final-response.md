I added `certbot_staging` (default `false`) and made the certificate request skip domains that already have a live certificate. None of it has been run against certbot or a host; the only check was `ansible-lint`.

**What changed**
- **Variable:** `certbot_staging: false` is in `defaults/main.yml`, and `README.md` has a new row for it. When it's true, `--staging` is added to the `certbot certonly` command.
- **Skip logic:** a certificate request is skipped for any domain whose certificate output contains `(VALID`.
- **Lint:** `ansible-lint` flags only `risky-file-permissions` on the renewal timer task. That task was already there and I left it alone.

**Beyond what you asked**
- **Per-domain count:** I changed the collection task. The old one counted `VALID` across all certificates, so one valid certificate would have skipped every domain. It now runs `certbot certificates -d <domain>` for each domain and checks each result separately.
- **Pipe removed:** the old `shell: ... | grep -c` also failed the play when nothing matched, because `grep -c` exits 1 on zero matches. I dropped the pipe and count the matches in the `when:` condition, so there is no pipe for lint to flag.
- **Task flags:** the collection task has `changed_when: false` and `check_mode: false`. The request task has `changed_when: true`. Without that last one, `ansible-lint` flags the request task for having no `changed_when`.

**Matching `(VALID` rather than `VALID`:** a plain `VALID` also matches `INVALID: TEST_CERT`, which is how certbot labels staging certificates. A staging run would then have counted as a live certificate and blocked the real request. The README row notes that staging certificates don't count as valid.
