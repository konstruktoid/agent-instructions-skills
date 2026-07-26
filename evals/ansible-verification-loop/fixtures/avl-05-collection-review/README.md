# platform.firewall

Firewall roles for Debian and RedHat hosts.

## Roles

| Role | Purpose |
|------|---------|
| `nftables_base` | Applies a base nftables ruleset. |

## Testing

```sh
make test
```

`make test` runs `ansible-lint` and then the molecule scenario.
