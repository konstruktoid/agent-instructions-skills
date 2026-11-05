I rewrote both variable descriptions in `variables.tf` and fixed three typos in `README.md`. I didn't run `make test` or any other tests. Only description strings and prose changed, so I didn't add or change any tests. `terraform fmt -check` printed nothing, so formatting is fine.

- **`name`:** now reads "Name of the service the retention policy applies to. Also used as the prefix of the policy_name output."
- **`retention_days`:** now reads "Number of days the service's data is retained under the policy."
- **README typos:** "smal" is now "small", "polcy" is now "policy", and "formating" is now "formatting".

The `retention_days` wording is my reading of the name. Nothing in `main.tf` says what the number is actually applied to, so check that "data is retained" is what you mean.
