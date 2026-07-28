Lint passes clean. Summary of changes:

- `defaults/main.yml`: added `banner_country_code: "NO"` and `banner_gateway_ports: false`.
- `templates/issue.net.j2`: renders a `Country:` line and a gateway-ports permission statement.
- `README.md`: documented both new variables in the role variables table.
