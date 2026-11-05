I rewrote both variable descriptions in `variables.tf` and fixed the three typos in `README.md`. I didn't run `terraform test` or `make test`. The edits only touch description strings and prose, so no types, defaults or other behavior changed, and I didn't add a test.

- **`name`:** the description is now "Name of the service the retention policy is recorded for."
- **`retention_days`:** the description is now "Number of days the service's data is retained under the policy."
- **README typos:** "smal" is now "small", "polcy" is now "policy", and "formating" is now "formatting".

I inferred what each variable controls from the README and the variable names, since nothing else in the repo uses them. Check that the `retention_days` wording matches what the module really does with that value.
