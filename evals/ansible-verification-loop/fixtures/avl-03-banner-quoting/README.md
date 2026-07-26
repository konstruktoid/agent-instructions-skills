# login_banner

Renders the pre-authentication login banner.

## Role variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `banner_path` | `/etc/issue.net` | Where the banner is written. |
| `banner_owner` | `root` | Owner and group of the banner file. |
| `banner_mode` | `"0644"` | File mode of the banner. |
| `banner_show_hostname` | `true` | Whether the banner includes the hostname. |
