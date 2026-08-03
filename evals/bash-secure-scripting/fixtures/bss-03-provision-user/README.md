# provisioning

Account provisioning for the application hosts.

`sbin/provision-user.sh USERNAME` creates the local account and its database user. It runs
as root from `etc/cron.d/provision`. Database administrator credentials live in
`etc/db.conf`.
