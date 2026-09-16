Renders correctly and `banner_country_code` parses as the string `"NO"` (not YAML's boolean `no`), confirming the quoting is doing its job.

Files changed:
- `defaults/main.yml` — added `banner_country_code: "NO"` and `banner_gateway_ports: false`
- `templates/issue.net.j2` — added `Country:` line and gateway-ports permitted/not-permitted lines
- `README.md` — documented both new variables in the variable table

Verified YAML parses correctly and the Jinja2 template parses and renders as expected (no ansible-lint/ansible-playbook available in this environment to run the full role lint/check).
