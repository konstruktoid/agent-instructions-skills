Done. Changed files:

- `defaults/main.yml` — added `banner_country_code: "NO"` (quoted: unquoted `NO` resolves to boolean `false` under Ansible's YAML 1.1 loader) and `banner_gateway_ports: false`.
- `templates/issue.net.j2` — renders `Country: {{ banner_country_code }}` unconditionally and a "Gateway ports are permitted." line when `banner_gateway_ports` is true.
- `README.md` — documented both variables in the role variables table.

No `meta/argument_specs.yml` or test/molecule scaffolding exists in this role, so nothing there needed updating. `ansible-lint` (moderate profile) is clean, and I confirmed the rendered output directly via `ansible-playbook --check --diff`: default run shows `Country: NO` with no gateway-ports line, and `banner_gateway_ports=true` adds the line — verifying the quoting fix actually works, not just that the YAML parses.
