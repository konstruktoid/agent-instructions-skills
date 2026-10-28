Both commands talk to real infrastructure, but they do different jobs.

## `terraform plan`
- **Purpose:** Works out what Terraform would do to make the real infrastructure match your configuration.
- **What it compares:** Your `.tf` files against the state, after a refresh. By default, plan first refreshes its in-memory copy of the state from the real infrastructure.
- **Output:** A list of proposed create, update, replace and destroy actions. It also reports "objects have changed outside of Terraform" when it detects drift.
- **Side effects:** None. It changes neither the state nor the infrastructure. You can save the result with `-out=planfile` and apply exactly that plan later.

## `terraform apply -refresh-only`
- **Purpose:** Updates the **state file** to match what actually exists right now. It does not touch the infrastructure.
- **What it compares:** The current state against the real infrastructure. **Your configuration is not used to propose changes.**
- **Output:** A list of differences between state and reality, such as an attribute someone edited in the console or a resource deleted outside Terraform. It then asks whether to write those values into state.
- **Side effects:** Only the state changes. No resources are created, modified or destroyed.
- There's also a preview-only form, `terraform plan -refresh-only`, which shows the drift without writing anything.

## Key differences

| | `terraform plan` | `terraform apply -refresh-only` |
|---|---|---|
| Uses your config to propose changes | Yes | No |
| Changes infrastructure | No (`apply` does that) | Never |
| Changes state | No | Yes, after you confirm |
| Main question it answers | "What will Terraform change to match my code?" | "What has changed outside Terraform, and should state record it?" |

## When to use which
- **`plan`:** Before every normal change, to review what applying your config would do.
- **`apply -refresh-only`:** When you know drift has happened and want state to accept reality, for example after an emergency manual fix you intend to keep.
  - After that, update your config to match. Otherwise the next `plan` will propose undoing the drift.
  - It replaced the deprecated `terraform refresh`. `terraform refresh` writes to state with no review step; the new form shows the changes and asks for confirmation.

## Caveats
- **Deleted resources:** If a resource was deleted outside Terraform, refresh-only removes it from state. That can quietly hide a problem, so read the proposed changes before confirming.
- **Credentials and sensitive data:** Both commands read live resources, so both need provider credentials with read access. Both can also put sensitive values into state or plan output, so handle those artifacts with the same care as the state file.
