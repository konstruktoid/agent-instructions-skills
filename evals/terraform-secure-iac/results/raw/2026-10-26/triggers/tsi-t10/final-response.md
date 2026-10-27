**`terraform plan`** compares three things: your configuration, the state file, and (by default) the real infrastructure. It refreshes state in memory, then proposes changes to make reality match your *configuration*. It's a preview. It writes nothing to state, and it can be saved with `-out` and applied later.

**`terraform apply -refresh-only`** ignores configuration changes. It only reconciles the *state file* with real infrastructure. It queries the providers, shows you the drift (resources changed, or deleted outside Terraform), and, once you approve, writes those observed values into state. It never creates, modifies, or destroys infrastructure.

Key differences:

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Goal | Make infrastructure match config | Make state match infrastructure |
| Considers config changes | Yes | No |
| Modifies real infrastructure | No (only proposes) | Never |
| Writes to state | No | Yes, after approval |
| Needs confirmation | No | Yes (unless `-auto-approve`) |

Related points:

- **Old `terraform refresh`** was the predecessor of `apply -refresh-only`. It wrote to state immediately with no review step, which is why it was deprecated. The new form shows the diff first.
- **`terraform plan -refresh-only`** previews the same drift report without writing anything. It's the safe way to inspect drift before committing to the state update.
- **Drift handling:** with a plain `plan`, drift is detected, but Terraform will try to revert it if the config disagrees. With `-refresh-only`, you're accepting the drift into state. If the config doesn't match the new state, the next `plan` will then show a diff to revert it.
- **Security note:** since refresh-only writes real attribute values into state, which can include sensitive data, make sure the state backend is encrypted and access-controlled.

Typical use: a teammate changed a tag or resized something in the console. Run `plan -refresh-only` to see it, then `apply -refresh-only` to record it. Alternatively, run a normal `plan`/`apply` to revert it back to what the config says.
