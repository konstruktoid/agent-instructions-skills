`terraform plan` previews changes to your infrastructure. `terraform apply -refresh-only` changes nothing in your infrastructure. It only updates the state file so it matches what actually exists.

## `terraform plan`

1. **Refresh (in memory):** reads the current real-world attributes of every resource in state from the provider APIs.
2. **Diff:** compares your configuration with that refreshed view.
3. **Proposes actions:** create, update, replace or destroy, so the infrastructure ends up matching your code.

It writes nothing to state or to infrastructure. The refreshed data only exists for that run. Drift it finds shows up as "Objects have changed outside of Terraform," and the planned actions then work to undo that drift.

## `terraform apply -refresh-only`

1. **Refresh:** same reading of real-world attributes.
2. **Shows a drift report:** which attributes changed outside Terraform, and which resources no longer exist.
3. **After you approve, writes the refreshed values into state.** It proposes no changes to infrastructure.

It never looks at your configuration to plan changes. The point is to accept drift into state, not to fix it.

## Side by side

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Reads real infrastructure | Yes | Yes |
| Compares against your configuration | Yes | No (state vs. reality only) |
| Proposes infrastructure changes | Yes | Never |
| Modifies state | No | Yes, after approval |
| Modifies infrastructure | No | No |

## When to use which

- **`plan`**: before any change, in CI on pull requests, or to see what `apply` would do.
- **`apply -refresh-only`**: when someone changed something by hand (console edit, autoscaling, an external tool), you want Terraform to accept the new values, and you'll update your code to match afterwards. Without that code update, the next `plan` will propose reverting the change.
- **`plan -refresh-only`**: a preview of the drift report that writes nothing. It's a safe way to check for drift.

## Things to watch

- **It replaces the old `terraform refresh`.** That command did the same thing but updated state without asking. `apply -refresh-only` shows you the changes and asks for approval first.
- **Deleted resources disappear from state.** If a resource was deleted, or is temporarily unreachable (wrong credentials, wrong region), it gets dropped from state. Read the drift report carefully before approving.
- **State can hold secrets.** Refreshing can write new values into state, including sensitive ones. Keep your backend encrypted and access-controlled.
- **`plan -refresh=false`** is the opposite: it skips the refresh and diffs against the state as stored. It's faster, but it won't notice drift.
