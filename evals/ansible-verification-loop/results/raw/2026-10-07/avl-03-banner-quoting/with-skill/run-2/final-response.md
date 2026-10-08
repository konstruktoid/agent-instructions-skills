I added both variables to the role. I rendered them in the template and documented them in the README.

- **`banner_country_code`:** the default is `"NO"`, and the banner gets a `Country: NO` line. The default is quoted in `defaults/main.yml`. Ansible reads YAML 1.1, so an unquoted `NO` would become boolean `false`. The README says to keep it quoted.
- **`banner_gateway_ports`:** the default is `false`. When it is true, the banner adds the line `Gateway ports are permitted.` When it is false, that line is left out. The README notes that this only changes the banner text and not the SSH configuration.

**Verification**
- `ansible-lint` passed before and after the change, with 0 failures and 0 warnings both times.
- I applied the role to localhost with the defaults. The banner had `Country: NO` and no gateway line.
- I applied it again with `SE` and gateway ports on. The banner had `Country: SE` and `Gateway ports are permitted.`
- Both test runs used `banner_owner: user` because the root chown fails in this sandbox. The role's own default owner is unchanged.

**Not covered**
- The role has no `meta/argument_specs.yml` and no molecule scenario, so there was nothing to update there. I didn't create either, and I ran no molecule tests.
- Only the three tracked files changed: `defaults/main.yml`, `templates/issue.net.j2` and `README.md`.
