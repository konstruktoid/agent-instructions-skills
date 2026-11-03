`terraform plan` shows you what changes would make your real infrastructure match your configuration. `terraform apply -refresh-only` doesn't touch your infrastructure or look at your configuration's intended changes. It only updates the **state file** so it matches what actually exists.

## `terraform plan`

1. **Refreshes** a copy of the state in memory by asking the provider APIs what each managed resource looks like now. Nothing is saved.
2. **Compares** that refreshed view against your `.tf` configuration.
3. **Proposes actions** (create, update in place, replace, destroy) that would make real infrastructure match the configuration.
4. **Changes nothing.** It doesn't touch infrastructure and doesn't write state, unless you save the plan with `-out` and apply it later.

If plan detects drift, it reports it under "Objects have changed outside of Terraform." It then plans to **revert** that drift back to what the config says.

## `terraform apply -refresh-only`

1. **Refreshes** state by reading real infrastructure, the same as above.
2. **Ignores the configuration's desired changes.** It never proposes creating, updating or destroying resources.
3. Shows you the differences between the old state and reality, then asks for approval.
4. On approval, **writes the new values to the state file.** Infrastructure is never modified.

It effectively **accepts drift**: Terraform's record now reflects reality as it is. A resource that was deleted outside Terraform is removed from state. Attributes changed by hand are recorded with their new values.

## Side by side

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Reads real infrastructure | Yes | Yes |
| Uses the config's desired state | Yes | No |
| Modifies infrastructure | Never | Never |
| Writes the state file | No | Yes, after approval |
| What it does with drift | Plans to revert it to match the config | Records it in state as the new truth |

## Related variants

- **`terraform plan -refresh-only`**: a dry run of the above. It shows what the refresh would change in state without writing anything.
- **`terraform plan -refresh=false`**: skips the refresh and plans against the state as stored. This is faster but blind to drift.
- **`terraform refresh`**: the older command. It's equivalent to `apply -refresh-only -auto-approve` and is deprecated because it writes state without letting you review it first.

## When to use which

- **Use `plan`** before any change, to see what Terraform will do to your infrastructure. It's also how you spot drift you want to undo.
- **Use `apply -refresh-only`** when someone changed something outside Terraform and you want to accept that change. For example, an emergency console fix, or a resource deleted manually. After that, update your `.tf` files to match. Otherwise the next `plan` will propose reverting the change.

**Caution:** read the refresh-only plan carefully before approving. If a resource looks "deleted" only because of a credentials or region mistake, approving removes it from state. Terraform then stops managing it, and a later `apply` may try to create a duplicate. The state may also store new sensitive attribute values read from the provider, so the state backend needs to stay properly protected.
