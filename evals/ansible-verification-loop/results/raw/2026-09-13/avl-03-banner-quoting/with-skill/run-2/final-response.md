No leftover state, nothing untracked.

**Changed:** `defaults/main.yml`, `templates/issue.net.j2`, `README.md`.

- `banner_country_code` defaults to `"NO"` — quoted deliberately, since Ansible's PyYAML loader follows YAML 1.1 and would otherwise resolve unquoted `NO` as boolean `false` (the "Norway problem").
- `banner_gateway_ports` defaults to `false` (real boolean, consistent with `banner_show_hostname`).
- Template renders `Country: {{ banner_country_code }}` unconditionally and `Gateway ports are permitted.` only when `banner_gateway_ports` is true.
- README table documents both.

`ansible-lint` (profile `moderate`, effectively `production`) passes clean, output identical before and after the change. No `meta/argument_specs.yml` or molecule/tox harness exists in this fixture role, so lint plus manual YAML-load verification is the full check available. No unrelated files touched, nothing untracked left behind.
