I added both variables, and they render correctly in a test run. `ansible-lint` passes.

- **`banner_country_code`**: it defaults to `"NO"` in `defaults/main.yml`, and the template renders it as a `Country:` line. I quoted the default on purpose. YAML 1.1 reads an unquoted `NO` as boolean `false`, so the banner would have shown `Country: False`. There's a comment in the defaults file, and the README tells users to keep the value quoted.
- **`banner_gateway_ports`**: it defaults to `false`. When it's true, the template adds a `Gateway ports: permitted` line. When it's false, the line is left out.
- **README**: I added a row for each variable to the role variables table.

I rendered the template with the defaults and with `banner_gateway_ports: true` and `banner_country_code: SE`, using a private temp directory. The defaults gave `Country: NO` with no gateway line. The override gave `Country: SE` and `Gateway ports: permitted`.

I didn't run the role's own `tasks/main.yml`. Its `chown` to `root` isn't permitted for this user. I haven't committed anything.
