I added both variables, rendered them in the banner and documented them in the README. `ansible-lint` passes before and after, with no warnings. A local converge shows the new output, but I didn't re-run it to check idempotence.

- **`banner_country_code`** defaults to `"NO"` in `defaults/main.yml`. I quoted it because Ansible's YAML loader reads an unquoted `NO` as boolean false. The template renders it as a `Country: NO` line.
- **`banner_gateway_ports`** defaults to `false`. When it's true, the banner gets the line "Gateway ports are permitted." When it's false, the line is left out.
- **README:** both variables have rows in the variables table. The country code row explains the quoting. The gateway row says the variable only changes the banner text and doesn't change the SSH configuration.

I converged the role locally against localhost. With the defaults, the banner shows `Country: NO` and no gateway line. With `banner_gateway_ports=true`, it also shows the gateway line.

The repo has no molecule scenarios, tox config or `meta/argument_specs.yml`, so there were no test fixtures or argument specs to update. The only checks were `ansible-lint` and the manual converge.
