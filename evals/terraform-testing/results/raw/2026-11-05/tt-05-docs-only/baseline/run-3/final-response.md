I rewrote both variable descriptions in `variables.tf` and fixed three typos in `README.md`. I didn't run `make test` or any Terraform commands. Only description strings and prose changed, so behavior is unchanged.

- **`name`:** the description now reads "Name of the service the retention policy applies to."
- **`retention_days`:** it now reads "Number of days the service's data is retained before it expires. Defaults to 30."
- **`README.md`:** "smal" is now "small", "polcy" is now "policy", and "formating" is now "formatting".

I inferred what the variables control from their names and the README's description of the module. I didn't check how they're used, because the workspace has no other `.tf` files. If `retention_days` means something more specific than data retention, adjust that wording.
