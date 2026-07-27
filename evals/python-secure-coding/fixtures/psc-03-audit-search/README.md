# auditlog

Searches the audit log.

## Usage

```sh
PYTHONPATH=src python -m auditlog.search --actor alice --action login
```

`--sort` and `--direction` select the ordering column and direction; both default
to a timestamp descending sort. Results are unpaginated.

Clause building lives in `auditlog.filters`, so the same escaping and ordering
rules apply to every query against the table.
