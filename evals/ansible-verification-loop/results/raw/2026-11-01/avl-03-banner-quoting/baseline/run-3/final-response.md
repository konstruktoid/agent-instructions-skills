I added both variables to the role and checked them by rendering the template.

- **`banner_country_code`**: it defaults to `"NO"` in `defaults/main.yml`, and the template renders it as a `Country:` line. I quoted the value because an unquoted `NO` is read as boolean false in YAML 1.1. The README notes this.
- **`banner_gateway_ports`**: it defaults to `false`. When it's true, the banner gets a `Gateway ports: permitted` line. When it's false, no gateway ports line appears.
- **README**: both variables have rows in the role variables table.

I rendered the template with the defaults and with `banner_gateway_ports` set to true. The defaults gave `Country: NO` and no gateway line, and the true case added `Gateway ports: permitted`. `ansible-lint` passes.

I haven't committed anything.
