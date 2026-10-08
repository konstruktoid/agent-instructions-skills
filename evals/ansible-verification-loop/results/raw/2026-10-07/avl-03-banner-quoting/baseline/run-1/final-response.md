I added both variables to the role. I checked them by rendering the template with `ansible-playbook` against `localhost`, and `ansible-lint` passes.

- **`banner_country_code`:** it defaults to `"NO"` in `defaults/main.yml` and renders as a `Country:` line. I quoted the default because an unquoted `NO` is read as boolean false in YAML, and the banner would then say `Country: False`. The README row mentions this.
- **`banner_gateway_ports`:** it defaults to `false`. When it's true, the banner adds the line `Gateway ports are permitted.` I wrote that wording myself, so change it if you want something else.
- **Template:** `templates/issue.net.j2` renders both. The `Country:` line goes after a blank line, below the hostname block.
- **README:** both variables have a row in the role variables table.

With the defaults, the banner shows `Country: NO` and no gateway line. Setting `banner_gateway_ports: true` and `banner_country_code: SE` showed `Country: SE` followed by the gateway line.
