**`terraform plan`** is a read-only preview of what Terraform would change to make real infrastructure match your configuration. It refreshes state in memory, compares it to your config, and shows proposed create/update/destroy actions. It writes nothing to state and changes no infrastructure. (You can save the result with `-out` for a later `apply`.)

**`terraform apply -refresh-only`** reconciles the *state file* with real infrastructure, without proposing any changes to the infrastructure itself. It:

- Queries the real resources and detects drift (changes made outside Terraform, such as console edits).
- Shows you the differences between state and reality.
- After you approve, **writes the updated values to state** (and updates outputs).
- Never creates, modifies, or destroys remote resources, and ignores differences between config and state.

**Key differences**

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Goal | Make infra match config | Make state match infra |
| Changes state file | No | Yes (after approval) |
| Changes infrastructure | No (only previews) | No |
| Considers config changes | Yes | No |
| Typical use | Review pending changes | Accept known drift into state |

**Context**

- `-refresh-only` replaces the deprecated `terraform refresh`. That command updated state immediately with no review step. The new mode shows the diff and asks for approval first.
- `terraform plan -refresh-only` previews the same drift detection without writing state. It is the safe first look before running `apply -refresh-only`.
- Plain `plan` and `apply` already refresh by default. So after you accept drift with `-refresh-only`, a normal `plan` will show the changes needed to revert that drift back to your config, unless you update the config to match.
- Because it writes state, `apply -refresh-only` can store new values, including sensitive ones, in state. That is another reason to keep state in a protected, encrypted backend.
