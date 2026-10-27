**`terraform plan`** works out what Terraform would need to change in real infrastructure to make it match your configuration.

- By default it refreshes first: it reads the current state of every resource in state from the providers.
- It then compares that refreshed state with your `.tf` configuration and proposes create, update, replace and destroy actions.
- It doesn't write anything, to state or to infrastructure. With `-out=tfplan` it saves the proposal so a later `terraform apply tfplan` runs exactly those actions.
- Use it when you've changed configuration and want to see what will change.

**`terraform apply -refresh-only`** updates the state file to match real infrastructure, without changing any infrastructure.

- It reads every resource from the providers and compares what it finds with the state file. Your configuration isn't used as a target.
- It shows the drift, for example "tags changed outside Terraform" or "this instance no longer exists". After you approve, it writes those values into state.
- It never creates, modifies or destroys real resources. It also updates root module outputs.
- Use it when someone changed things outside Terraform (console edits, autoscaling, manual deletes) and you want state to record that before deciding what to do next.

**Side by side**

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Compares | Real infra vs. **configuration** | Real infra vs. **state** |
| Changes infrastructure | No (shows what `apply` would do) | Never |
| Changes state | No | Yes, after approval |
| Answers | "What will Terraform change?" | "What changed without Terraform, and should state record it?" |

**Related commands**

- **`terraform plan -refresh-only`** shows the same drift report without writing to state. Run it to review before you commit with `apply -refresh-only`.
- **`terraform refresh`** is the deprecated older form. It does the same thing as `apply -refresh-only -auto-approve`, which means it updates state with no review step. That's riskier: if credentials point at the wrong account or region, resources can look deleted and drop out of state silently.
- **`plan -refresh=false`** skips the refresh step and compares configuration against state as last recorded. It's faster, but it misses drift.

**A typical drift workflow:** run `plan -refresh-only` to see what drifted. If the outside change should stay, run `apply -refresh-only` to accept it into state, then update your config so it matches. If it shouldn't stay, run a normal `plan` and `apply` to put things back the way the configuration says.
