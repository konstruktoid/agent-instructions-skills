#!/bin/bash
# Restart a service on the deploy host and announce the release.

set -e

SERVICE=$1
VERSION=$2

REMOTE_HOST=deploy@deploy.example.internal
SLACK_URL=$SLACK_WEBHOOK_URL

. etc/services.conf

# Per-service override, for example CONFIG_web=/etc/web/deploy.conf
eval "CONFIG=\$CONFIG_$SERVICE"

echo "deploying $SERVICE $VERSION with $CONFIG"

ssh $REMOTE_HOST "sudo systemctl restart $SERVICE && /usr/local/bin/deploy $SERVICE $VERSION"

curl -s -X POST -H 'Content-type: application/json' \
  -d "{\"text\": \"Deployed $SERVICE $VERSION by $USER\"}" $SLACK_URL
