#!/bin/bash
# Nightly backup of the application data directory.

DATA_DIR=/srv/ledger/data
TARGET=/mnt/backup

TMP=/tmp/backup.$$
mkdir $TMP

tar czf $TMP/data.tar.gz $DATA_DIR
scp $TMP/data.tar.gz backup@archive.example.internal:$TARGET/data-`date +%F`.tar.gz

rm -rf $TMP
