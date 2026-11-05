I made both changes. I didn't run `make test` or `terraform fmt`, so the formatting check hasn't run.

**`variables.tf`**
- `name` now reads "Name of the service the retention policy applies to."
- `retention_days` now reads "Number of days the service's data is retained under the policy."

I inferred what each variable controls from the module's description in the README and from the variable names. I didn't check how they're used elsewhere. If `retention_days` means something more specific, such as logs only, the wording needs adjusting.

**`README.md`**
- "smal" is now "small".
- "polcy" is now "policy".
- "formating" is now "formatting".

Only the description strings and README prose changed. Types, defaults and everything else in the module are untouched.
