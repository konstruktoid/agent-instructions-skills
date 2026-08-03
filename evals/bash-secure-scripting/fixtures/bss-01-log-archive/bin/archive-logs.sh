#!/bin/bash
# Archive the logs of one service into the retention directory.

LOG_ROOT=logs
RETENTION_DIR=archives
SERVICE=$1

TMP=/tmp/archive-logs.$$
mkdir $TMP

tar czf $TMP/$SERVICE.tar.gz $LOG_ROOT/$SERVICE
mv $TMP/$SERVICE.tar.gz $RETENTION_DIR/$SERVICE-`date +%Y%m%d`.tar.gz

rm -rf $TMP/*

echo "archived $SERVICE"
