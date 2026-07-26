# certbot_renewal

Requests and renews Let's Encrypt certificates.

## Role variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `certbot_domains` | `[]` | Domains to request certificates for. |
| `certbot_email` | `admin@example.com` | Registration contact address. |
| `certbot_renew_hour` | `3` | Hour the renewal timer fires. |
