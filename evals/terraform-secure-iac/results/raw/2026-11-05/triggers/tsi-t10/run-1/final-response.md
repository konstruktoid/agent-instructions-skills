**`terraform plan`** is a read-only preview of changes to make your infrastructure match your configuration.

- It refreshes state in memory (queries real infrastructure), compares it to your config, and shows the proposed create/update/destroy actions.
- It doesn't modify infrastructure or the state file. (Saved plan files via `-out` are just artifacts.)
- Its purpose is to answer "what would Terraform change to make reality match my code?"

**`terraform apply -refresh-only`** reconciles state with reality, without touching infrastructure.

- It reads the real infrastructure and shows where it has drifted from the state, for example from console edits or externally changed attributes.
- After you confirm, it **writes those observed values into the state file** (and updates root outputs). It never creates, changes, or destroys resources.
- Its purpose is to answer "what has changed outside Terraform, and should state accept it?"
- Config isn't used to propose changes. Drift is just recorded, so a later `plan` will show the diff between config and the updated state.

**Key differences**

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Changes infrastructure | No | No |
| Writes state | No | Yes, after approval |
| Compares | Config vs. refreshed state | Refreshed state vs. stored state |
| Shows | Actions needed to match config | Drift that will be recorded |
| Use for | Reviewing changes before apply | Accepting out-of-band changes into state |

**Related notes**

- `terraform plan -refresh-only` previews the same drift report without writing state. It's the safe way to inspect drift first.
- This replaced the deprecated `terraform refresh` command. That command updated state immediately with no review step, which was risky if credentials or the provider were misconfigured and resources appeared missing.
- Accepting drift into state doesn't fix it. If the config disagrees with the drifted value, the next `plan` will propose reverting it.
- Because state can contain sensitive values, remember that a refresh-only apply persists whatever the provider reads, including secrets, into state. Use a secured, encrypted remote backend.
