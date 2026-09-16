Renders correctly with the default `Country: NO` line and the gateway-ports statement toggling as expected. No Ansible/ansible-lint binary was present in this environment to run the full role, so verification was done via direct YAML-parse and Jinja2-render checks instead.

Files changed:
- `defaults/main.yml` — added `banner_country_code: "NO"` (quoted, avoiding the YAML Norway-problem boolean coercion) and `banner_gateway_ports: false`
- `templates/issue.net.j2` — renders `Country:` line and a gateway-ports permitted/not-permitted line
- `README.md` — documents both new variables in the variable table
