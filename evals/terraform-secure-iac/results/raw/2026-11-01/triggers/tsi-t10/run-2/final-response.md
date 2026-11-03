The two commands do different jobs. `terraform plan` works out how to make the real infrastructure match your configuration. `terraform apply -refresh-only` updates Terraform's state so it matches the real infrastructure, and it leaves the infrastructure alone.

## `terraform plan`

- **Refreshes in memory:** it reads the current attributes of every managed resource from the provider APIs. That refreshed state is used only for the comparison and isn't saved.
- **Compares the result to your `.tf` configuration** and proposes create, update, replace and destroy actions so the real infrastructure matches the configuration.
- **Read-only:** it changes neither the infrastructure nor the state file. You can save the proposal with `-out=tfplan` and apply exactly that plan later.
- **Drift:** if someone changed a resource outside Terraform, plan usually proposes changing it back to what the configuration says.

## `terraform apply -refresh-only`

- **Refreshes the same way:** it reads the current real-world attributes of every managed resource.
- **Ignores the configuration:** it doesn't compare against your `.tf` files and never proposes infrastructure changes.
- **Shows only state changes:** for example, "attribute X changed outside of Terraform" or "resource Y no longer exists".
- **Writes the state after approval:** once you approve, it saves those observed values into the state file. No cloud resources are created, changed or destroyed.
- **Drift:** it accepts out-of-band changes as the new truth in state, instead of reverting them.

## Side by side

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Question it answers | What would make the infrastructure match the config? | What does the infrastructure look like now? |
| Uses the `.tf` config to decide actions | Yes | No |
| Changes infrastructure | No (`apply` does that later) | Never |
| Changes the state file | No | Yes, after approval |
| Effect on drift | Proposes reverting it | Records it in state |

## Related commands

- **`terraform plan -refresh-only`** shows what a refresh-only apply would write to state, without writing anything. Use it to preview drift safely.
- **`terraform refresh`** is the deprecated older command. It wrote the refreshed state with no review step, so a misconfigured provider could silently make resources look deleted. `apply -refresh-only` replaced it because it shows the changes and asks for approval first.
- **`terraform plan -refresh=false`** goes the other way. It skips the refresh and plans from the saved state, which is faster but can miss drift.

## When to use which

- **Use `plan` (then `apply`)** when you've changed configuration, or when you want to enforce the configuration and undo manual changes.
- **Use `apply -refresh-only`** when an out-of-band change was intentional (for example, an emergency fix in the console) and you want state to reflect it. Afterwards, update your `.tf` files to match. Otherwise, the next normal `plan` will propose reverting it.

A refresh-only apply writes whatever the provider reports into state. If the provider is pointed at the wrong account or region, resources can look deleted and be dropped from state. Review the proposed changes before approving, and check what the refresh writes, because state can contain secrets.
