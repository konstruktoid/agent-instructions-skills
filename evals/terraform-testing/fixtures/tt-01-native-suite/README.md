# retention-policy

A small module that records a retention policy for one service.

## Tests

- `tests/unit/` holds one file per input or output, named for it, and every `run` block uses
  `command = plan`. `make test` formats and runs these.
- `tests/integration/` holds tests that `apply`. CI runs them with `make integration` in a sandbox
  account, and nobody adds to them without the platform team.
