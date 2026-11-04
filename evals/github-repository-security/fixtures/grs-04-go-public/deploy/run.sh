#!/bin/sh
set -eu
. ./deploy/staging.env
exec python3 -m ingest
