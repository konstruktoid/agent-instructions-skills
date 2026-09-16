Verification passed: `ansible-lint` output is unchanged (clean, same file/warning counts) before and after, and rendering the template confirmed `banner_country_code` stays the string `"NO"` (not coerced to a boolean by YAML 1.1's Norway-problem resolution) and that `banner_gateway_ports` correctly toggles the new line. No test fixtures existed in this role to update.

Files changed:
- `defaults/main.yml` — added `banner_country_code: "NO"` (quoted, since unquoted `NO`/`no` resolves to boolean `false` under the YAML 1.1 rules PyYAML uses) and `banner_gateway_ports: false`
- `templates/issue.net.j2` — added the `Country:` line and a conditional gateway-ports line
- `README.md` — documented both new variables in the variable table

No `meta/argument_specs.yml` or molecule scenario exists in this role, so there was nothing else to update. You can `/clear` before starting anything unrelated.
