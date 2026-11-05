I rewrote both variable descriptions in `variables.tf` and fixed the three typos in `README.md`. I didn't run `terraform test`, since only description strings and prose changed. `terraform fmt -check -recursive` passes.

- **`name`:** the description is now "Name of the service the retention policy applies to. Also used as the prefix of the policy_name output."
- **`retention_days`:** the description is now "Number of days the service's data is retained under the policy." I inferred the "service's data" part from the module's purpose. Nothing in the code says what is being retained, so adjust it if that's wrong.
- **README typos:** "smal" is now "small", "polcy" is now "policy", and "formating" is now "formatting".

Types and defaults are unchanged, and I added no tests because behavior didn't change. I haven't committed anything.
