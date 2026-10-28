**`terraform plan`** shows what it would take to make real infrastructure match your configuration.

- It refreshes state by default: it reads the current attributes of every managed resource from the provider.
- It compares your configuration with that refreshed view and proposes create, update, replace or destroy actions.
- It changes nothing. It only displays the proposal. You can save it with `-out=planfile` and later run `terraform apply planfile` to carry it out.
- Changes made outside Terraform ("drift") show up as a note, "Objects have changed outside of Terraform." Terraform then plans to change the real objects back to match your configuration.

**`terraform apply -refresh-only`** brings the **state file** in line with real infrastructure. It doesn't touch the infrastructure itself.

- It runs the same refresh, but it plans no resource actions, even where configuration and reality differ.
- The only thing it proposes is updating state to record what actually exists: changed attributes, and resources deleted outside Terraform being dropped from state.
- Once you approve, it writes to state only. No cloud resources are created, changed or destroyed.
- It replaces the deprecated `terraform refresh`. The difference is that you get a review step and must approve, while `terraform refresh` rewrote state silently.
- `terraform plan -refresh-only` gives a read-only preview of the same thing.

**Side by side**

| | `terraform plan` | `terraform apply -refresh-only` |
|---|---|---|
| Reads real infrastructure | Yes | Yes |
| Compares with configuration | Yes | No |
| Proposes resource changes | Yes | No |
| Writes state | No | Yes, after approval |
| Modifies infrastructure | No | No |
| What it does with drift | Plans to undo it | Records it in state |

**When to use each**

- Use `plan` before any normal change, to see what `apply` will do.
- Use `apply -refresh-only` when someone changed something by hand and you want to keep that change. Record it in state, then update your configuration to match. If you skip the configuration update, your next `plan` will try to undo the change.

**Two cautions**

- If credentials or provider configuration are wrong, a resource can look like it's gone. Approving a refresh-only apply would then drop it from state, so read the proposed state changes before approving.
- Refreshed state can bring in new attribute values, including sensitive ones. Make sure your state backend has encryption and access controls that suit that data.
