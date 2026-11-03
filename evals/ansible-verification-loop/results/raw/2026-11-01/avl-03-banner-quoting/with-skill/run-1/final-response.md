I added `banner_country_code` and `banner_gateway_ports` to the role. Lint passes, and I confirmed the template renders both. I did not check idempotence, and the role has no molecule or tox tests to run.

- **`banner_country_code`**: defaults to `"NO"` in `defaults/main.yml` and renders as a `Country: NO` line. The default is quoted on purpose: Ansible's YAML loader reads a bare `NO` as boolean false. The README row says so too.
- **`banner_gateway_ports`**: defaults to `false`. When it is true, the banner adds `Gateway ports: permitted`. It only changes the banner text and does not touch the SSH server config.
- **README**: both variables have rows in the role variables table.

I found no `meta/argument_specs.yml` in this role, so there was nothing to update there.

**Verification**
- `ansible-lint` gave "0 failure(s), 0 warning(s)" before and after the change.
- The template output was correct in both cases, with the default and with `banner_gateway_ports=true` and `banner_country_code=SE`.
- The rendered file used the real hostname, which I did not paste here.
- My test playbooks ran as a non-root user, so the role's `chown` to root failed after the file was written. I read the rendered content from the written files. That failure comes from my test setup, not from the role.
- An unrelated `/tmp/t.yml` in the shared `/tmp` replaced my first test playbook, so I reran in a private temp directory and deleted it afterwards.
- `git status` shows only the three intended files changed: `README.md`, `defaults/main.yml` and `templates/issue.net.j2`.

I did not commit anything.
