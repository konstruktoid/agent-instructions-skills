I added both variables to the role and checked them by rendering the template. The repo has no molecule, tox or other test setup, so there was no test suite to run. `ansible-lint` passed before and after the change, with 0 failures and 0 warnings.

- **`banner_country_code`:** it defaults to `"NO"` in `defaults/main.yml`. The quotes matter: an unquoted `NO` is read by YAML as boolean `false`, so the quoted default is what keeps it as Norway's country code. The README says this too. The template renders it as a `Country:` line.
- **`banner_gateway_ports`:** it defaults to `false`. When true, the template adds a `Gateway ports: permitted` line. When false, the line is left out.
- **README:** both variables have rows in the variables table.

I rendered the role to a temporary file. With gateway ports off, the output has `Country: NO` and no gateway line. With it on, the gateway line appears. My first test run passed `-e banner_gateway_ports=false`, which Ansible reads as the string `"false"`, so both runs wrongly showed the line. I reran with JSON extra-vars and got the results above. The role isn't affected, but if you override the variable from the command line, pass a real boolean, for example `-e '{"banner_gateway_ports": false}'`.

The role has no `meta/argument_specs.yml`, so there was nothing to update there. The working tree has only the three intended changes, and I removed my temporary test files.

I made no commit.
