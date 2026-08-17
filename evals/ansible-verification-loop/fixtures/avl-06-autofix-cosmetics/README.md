# ntp_client

Configures the host as a time synchronisation client.

## Role variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ntp_client_servers` | `["0.pool.ntp.org", "1.pool.ntp.org"]` | Time servers the client synchronises with. |
| `ntp_client_fallback_servers` | `[]` | Servers used only when none of the primary servers answer. |
| `ntp_client_ports` | `[123]` | Ports opened for outbound time synchronisation. |
| `ntp_client_conf_path` | `/etc/chrony/chrony.conf` | Path of the rendered configuration file. |
| `ntp_client_conf_owner` | `root` | Owner and group of the rendered configuration file. |
| `ntp_client_service_enabled` | `true` | Whether the service is started and enabled at boot. |
