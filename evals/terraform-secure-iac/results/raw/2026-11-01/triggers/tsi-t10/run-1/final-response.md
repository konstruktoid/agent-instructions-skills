Both commands look at the real infrastructure. They differ in what they're trying to change.

## `terraform plan`

- **Purpose:** shows the changes needed to make real infrastructure match your configuration.
- **Process:**
  1. Refreshes its view of real resources in memory (unless you pass `-refresh=false`).
  2. Compares that view to your `.tf` configuration.
  3. Proposes creates, updates and deletes.
- **Changes nothing:** neither state nor infrastructure. It's a dry run, though you can save it with `-out` and apply it later.
- **Drift:** if someone changed a resource by hand, `plan` proposes putting it back the way your config says.

## `terraform apply -refresh-only`

- **Purpose:** updates the **state file** to match real infrastructure. Your configuration is not used to propose any changes.
- **Process:**
  1. Reads the current attributes of every resource in state from the provider.
  2. Shows how the recorded state differs from reality. This is reported as changes "outside of Terraform."
  3. After you approve, writes those values into state.
- **Changes state only.** It never creates, modifies or destroys real resources.
- **Drift:** it accepts the drift. State now reflects the manual change, so a later `plan` compares your config against the drifted values.

## Side by side

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Reads real infrastructure | Yes | Yes |
| Compares against `.tf` config | Yes | No (resource changes aren't proposed) |
| Writes state | No | Yes, after approval |
| Modifies infrastructure | No | Never |
| Answers | "What would make reality match my code?" | "What does reality look like now?" |

## Related commands

- **`terraform plan -refresh-only`:** a dry run of the above. It shows the drift without writing state, so it's a good way to check for drift safely.
- **`terraform refresh`:** the deprecated older form. It works like `apply -refresh-only -auto-approve`, writing state with no review step. Avoid it, because a misconfigured provider can silently write bad data into state (for example, credentials for the wrong account or region can make resources look deleted).

## When to use which

- **To change infrastructure, or to see what a code change would do:** run `plan` (then `apply`).
- **When someone changed things outside Terraform and you want state to accept those changes:** run `apply -refresh-only`. Then update your `.tf` files to match, or the next `plan` will try to undo the drift.
- **To find out whether drift exists without changing anything:** run `plan -refresh-only`.
