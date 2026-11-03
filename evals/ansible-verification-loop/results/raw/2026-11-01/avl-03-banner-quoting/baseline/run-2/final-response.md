I added both variables to the role, rendered them in the template and documented them in the README.

- **`banner_country_code`:** it defaults to `"NO"` and renders as a `Country:` line. I quoted the default in `defaults/main.yml` because unquoted `NO` parses as boolean false in YAML 1.1. The README entry warns about this too.
- **`banner_gateway_ports`:** it defaults to `false`. When true, the banner gets a `Gateway ports: permitted` line.

I ran the role against localhost to check the output:
- **Defaults:** the banner shows `Country: NO` and no gateway line.
- **Overrides:** with `SE` and gateway ports on, it shows `Country: SE` and `Gateway ports: permitted`.
- **Owner override:** both runs needed `banner_owner` set to my own user, because I wasn't root and the role's default owner `root` makes the file task fail on chown.
- **Lint:** `ansible-lint` passes under the `moderate` profile.

The template doesn't check that the country code is a valid two-letter code, so any value is rendered as given.
