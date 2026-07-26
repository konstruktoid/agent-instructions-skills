Only the three intended files are modified. Verification checklist:

- **Lint**: `ansible-lint .` passes clean (production profile).
- **Behavior verified**: rendered a real playbook against the role's defaults — `banner_country_code` resolves as `type=str value=NO` (correctly quoted, avoiding the classic YAML 1.1 "Norway problem" where unquoted `NO` becomes boolean `false`), and `banner_gateway_ports` resolves as `type=bool value=False`. Output banner correctly showed `Country: NO` and `Gateway ports are not permitted.`
- No test suite (molecule/tox) exists in this fixture to update.
- No OS-conditional logic changed, so `meta/main.yml` needed no updates.
- No unrelated files changed.

## Summary
Added `banner_country_code` (defaults to `"NO"`, explicitly quoted to prevent Ansible's YAML 1.1 loader from reading it as boolean `false`) and `banner_gateway_ports` (defaults to `false`) to `defaults/main.yml`, rendered both in `templates/issue.net.j2` as a `Country:` line and a gateway-ports permitted/not-permitted line, and documented both in the README's variable table — including a note on why the country code must stay quoted.
