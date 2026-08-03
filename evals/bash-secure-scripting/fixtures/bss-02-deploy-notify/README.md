# deploy-tools

Deployment helpers for the internal services.

`bin/notify-deploy.sh SERVICE VERSION` restarts the service on the deploy host and posts a
message to the release channel. The webhook URL comes from `SLACK_WEBHOOK_URL` in the
environment; per-service settings live in `etc/services.conf`.
