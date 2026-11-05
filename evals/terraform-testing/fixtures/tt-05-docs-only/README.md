# retention-policy

A smal module that records a retention polcy for one service.

## Tests

- `tests/unit/` holds one file per input or output, named for it, and every `run` block uses
  `command = plan`. `make test` formats and runs these.
- `tests/integration/` holds tests that `apply`. CI runs them with `make integration` in a sandbox
  account, and nobody adds to them without the platform team.

Checks run with `make test`, which also checks formating.
