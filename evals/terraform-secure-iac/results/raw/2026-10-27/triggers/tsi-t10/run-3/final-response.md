Both commands refresh state by reading the real infrastructure, but they do different things with what they find.

## `terraform plan`
- **What it does:** Refreshes state in memory, then compares your **configuration** against that refreshed view. It proposes the create, update and destroy actions needed to make the infrastructure match your code.
- **Writes to state?** No. It's read-only unless you save the plan with `-out` and apply it later.
- **Question it answers:** "What would Terraform change to make the real infrastructure match my `.tf` files?"
- **Drift handling:** If someone changed a resource outside Terraform, the plan proposes changing it back to what the configuration says. It also shows the drift in a "changes outside of Terraform" section.

## `terraform apply -refresh-only`
- **What it does:** Reads the current attributes of every resource in state from the provider, and proposes updating the **state file** to match. It ignores your configuration when working out actions, so it never proposes creating, changing or destroying infrastructure.
- **Writes to state?** Yes, once you approve. The infrastructure itself is never touched.
- **Question it answers:** "What has changed out there since Terraform last recorded it, and should I accept that as the new baseline?"
- **Drift handling:** It records the drift in state instead of reverting it. On the next normal `plan`, Terraform compares your configuration against that updated state. So unless you also update your code, the next plan will still propose reverting the change.

## Side by side

| | `terraform plan` | `terraform apply -refresh-only` |
|---|---|---|
| Compares | config vs. refreshed real state | old state vs. real state |
| Can change infrastructure | No (only `apply` does) | Never |
| Persists state changes | No | Yes, after you approve |
| Typical use | Preview changes before `apply` | Accept or inspect drift; update outputs |

## Related commands
- **`terraform plan -refresh-only`** shows the same drift report without writing anything. It's the safe way to inspect drift first.
- **`terraform refresh`** is deprecated. It does the same as `apply -refresh-only -auto-approve`, writing to state with no review step. That's riskier: for example, if credentials point at the wrong region, resources can look deleted, and those removals get written to state without a chance to catch them.
- **`terraform plan -refresh=false`** skips the refresh and plans against the stored state as-is. It's faster but won't notice drift.

## Security note
Refreshing (with either command) pulls current attribute values from the provider. Those can include secrets such as generated passwords or connection strings. Only `apply -refresh-only` writes them to the state file. Before running it in CI, make sure the state backend is encrypted and access-controlled. Also review the proposed state changes, especially any resources shown as deleted, before approving.
