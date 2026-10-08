# fetchkit

A small HTTP client wrapper used by internal batch jobs.

## Timeouts

Every request times out after 30 seconds. The `--timeout` option of the batch runner takes a
number of seconds, so `--timeout 5` gives up after five seconds.
