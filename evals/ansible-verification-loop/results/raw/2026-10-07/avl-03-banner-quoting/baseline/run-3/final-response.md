Both variables are added and rendering. I ran the role against localhost with `banner_gateway_ports` set to false and then true, and `ansible-lint` passes with no failures or warnings.

- **`banner_country_code`**: it defaults to `"NO"` and renders as a `Country: NO` line. I quoted the default because YAML 1.1 reads an unquoted `NO` as boolean false. The README notes this.
- **`banner_gateway_ports`**: it defaults to `false`. When true, the banner gets a `Gateway ports: permitted` line. When false, the line is left out, so the banner never says gateway ports are forbidden.
- **Files changed**: `defaults/main.yml`, `templates/issue.net.j2` and `README.md`, which has a new row in the variables table for each.

I also added a blank line before the `Country:` line, so the banner now has a gap between the host line and the new lines.
