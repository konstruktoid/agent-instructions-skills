I added `certbot_staging` (default `false`) and made the certificate request skip when a valid certificate already exists. I didn't run the role, because there's no certbot environment here. `ansible-lint` still reports warnings, but none come from this change.

- **Staging flag:** `--staging` is appended to the `certbot certonly` command only when `certbot_staging` is true. It's defined in `defaults/main.yml` and documented in the README variable table.
- **Skip condition:** the request task runs only when `certbot_valid_count.stdout | int == 0`.
- **Extra fix:** the existing `grep -c "VALID"` task exits with code 1 when there are no matches, so the first run on a fresh host would have failed before reaching the request. I set `failed_when: certbot_valid_count.rc > 1` and `changed_when: false` on it.

The count covers all certificates on the host, not one domain. If any valid certificate exists, every domain's request is skipped, so a newly added domain won't get a certificate on a host that already has one for another domain. To check per domain, the collection task would need to run `certbot certificates -d <domain>` for each domain. I kept to the count the role already collects, as you asked, but I can change it.

The `ansible-lint` warnings are about FQCN, an unnamed task, pipefail, `changed_when` on the request task and file permissions. They were all there before this change and I left them alone.
