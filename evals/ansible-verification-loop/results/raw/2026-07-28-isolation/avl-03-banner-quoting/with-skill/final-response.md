Changes are scoped to exactly the three relevant files, ansible-lint passes clean at the required "moderate" profile, and I confirmed `banner_country_code`'s default (`"NO"`, Norway's ISO code) parses as the string `"NO"` rather than boolean `false` — the classic YAML 1.1 "Norway problem" that quoting avoids.

Summary of changes:
- `defaults/main.yml`: added `banner_country_code: "NO"` (quoted to avoid YAML 1.1 boolean coercion) and `banner_gateway_ports: false`
- `templates/issue.net.j2`: renders `Country: {{ banner_country_code }}` always, and a "Gateway ports are permitted." line conditionally on `banner_gateway_ports`
- `README.md`: documented both new variables in the variable table

No molecule/tox test scaffolding exists in this role, so `ansible-lint` was the applicable verification gate, and it passed clean.
