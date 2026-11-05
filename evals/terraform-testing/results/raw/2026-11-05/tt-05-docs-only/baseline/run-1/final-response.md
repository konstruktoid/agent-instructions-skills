I rewrote both variable descriptions in `variables.tf` and fixed three typos in `README.md`. I didn't run `make test` or any formatting check. Only description strings and prose changed, so behavior is the same.

**`variables.tf`**
- `name` now reads "Name of the service the retention policy applies to."
- `retention_days` now reads "Number of days the service's data is retained before it expires." The `retention_days` description assumes the value is a data-retention period. I didn't see the module's resources, so check that wording against what the module does with it.

**`README.md`**
- "smal" is now "small".
- "polcy" is now "policy".
- "formating" is now "formatting".
