I added both variables, and the rendered banner is correct. The playbook run did show a `chown failed` error, but that came from my test setup: I ran as a non-root user, so `chown` to `root` failed. The template rendered fine.

- **`banner_country_code`** defaults to `"NO"` and renders as a `Country: NO` line. I quoted the default in `defaults/main.yml` because an unquoted `NO` parses as boolean `false` in YAML 1.1. The README notes this.
- **`banner_gateway_ports`** defaults to `false`. When it's true, the banner adds a `Gateway ports: permitted` line. When it's false, nothing is added.
- **Files changed:** `defaults/main.yml`, `templates/issue.net.j2` and the README variables table.

I rendered the role to a temp file with default values, then again with `banner_gateway_ports=true`. The default output has `Country: NO` and no gateway line. The override adds `Gateway ports: permitted`. `ansible-lint` reports no failures or warnings.

I haven't committed anything.
