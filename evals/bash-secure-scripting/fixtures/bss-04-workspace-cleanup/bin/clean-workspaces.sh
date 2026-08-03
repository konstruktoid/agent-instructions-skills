#!/bin/bash
# Remove stale CI workspaces.

WORKSPACE_ROOT=workspaces
DAYS=7

cd $WORKSPACE_ROOT

for dir in $(ls); do
  if [ -d $dir ]; then
    LAST=`find $dir -type f -printf '%T@\n' | sort -n | tail -1`
    AGE=$(( ( $(date +%s) - ${LAST%.*} ) / 86400 ))
    if [ $AGE -gt $DAYS ]; then
      echo "removing $dir (age ${AGE}d)"
      rm -rf $dir/*
      rmdir $dir
    fi
  fi
done
