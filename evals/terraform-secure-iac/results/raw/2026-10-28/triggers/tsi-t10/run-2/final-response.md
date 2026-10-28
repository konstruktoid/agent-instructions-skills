They do different jobs. `terraform plan` works out what Terraform would change in your real infrastructure. `terraform apply -refresh-only` updates the state file to match your real infrastructure and changes nothing in the infrastructure itself.

## `terraform plan`

- **What it does:** It refreshes state in memory by reading the current attributes of each managed resource from the provider. It then compares your configuration against that refreshed view and proposes create, update or destroy actions so the infrastructure matches your code.
- **Side effects:** None. It doesn't write the state file and doesn't change infrastructure. You can save the plan with `-out=tfplan` and apply it later.
- **Drift:** If something changed outside Terraform, the plan reports it under "Objects have changed outside of Terraform". It then proposes actions to put the resource back to what your configuration says.

## `terraform apply -refresh-only`

- **What it does:** It reads the real attributes of each managed resource and updates the state file to match. It doesn't compare against your configuration to plan resource changes.
- **Side effects:** It writes the state file, after you confirm (unless you pass `-auto-approve`). It never creates, updates or destroys infrastructure. Root module outputs are updated too.
- **Drift:** It accepts the drift. Whatever is out there becomes the recorded truth in state.
- **Background:** This replaces the deprecated `terraform refresh`, which did the same thing without showing you anything or asking first.

## Side by side

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Reads real infrastructure | Yes | Yes |
| Compares against your configuration | Yes | No |
| Writes state | No | Yes, after you confirm |
| Changes infrastructure | No | Never |
| Result | Proposed changes to match the code | State updated to match reality |

`terraform plan -refresh-only` is the preview of the second command: it shows which state updates would happen without writing anything.

## Example

Someone adds a tag to an S3 bucket by hand in the console.

- **`terraform plan`** notes the drift and proposes removing the tag, because your configuration doesn't have it.
- **`terraform apply -refresh-only`** records the tag in state. Your next normal `plan` will still propose removing it unless you also add the tag to your configuration. Accepting drift into state doesn't make it part of your code.

## When to use which

- **`plan`:** Use it before every change, and to detect drift in CI with `-detailed-exitcode` (exit code 2 means there are changes).
- **`apply -refresh-only`:** Use it when the out-of-band change is legitimate and you want state to reflect it. It's also useful when a resource was deleted outside Terraform, because it removes that resource from state. Run `plan -refresh-only` first and check what will be written, since you can't take back a state write except by restoring an earlier state version.

## Related flag

`terraform plan -refresh=false` skips the refresh step and plans against the state as it stands. It's faster on large configurations, but it won't see any drift.
