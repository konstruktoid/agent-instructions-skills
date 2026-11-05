`terraform plan` previews changes to your infrastructure. `terraform apply -refresh-only` updates the state file to match what actually exists. They differ in what they compare and in what they change.

**`terraform plan`**
- It refreshes state by reading the real infrastructure. It then compares your configuration (the `.tf` files) to that refreshed state and proposes create, update, and destroy actions.
- It changes nothing, neither infrastructure nor state. With `-out`, it only saves a plan file.
- Use it to see what `apply` would do to make reality match your code.

**`terraform apply -refresh-only`**
- It reads the real infrastructure and compares it to the state file. It ignores your configuration, so it never proposes changes to resources.
- It shows the drift it found, such as a tag edited in the console, a changed attribute, or a deleted resource. It then asks for approval.
- On approval, it writes the real values into the state file. It does not touch infrastructure.
- Use it to accept drift into state deliberately, for example after an out-of-band change you want to keep.

**Why this matters**
- The old `terraform refresh` command did the same thing as `apply -refresh-only`, but without a review step and with no confirmation. It could silently overwrite state, for instance after you pointed it at the wrong credentials. `-refresh-only` shows the proposed state changes and asks for approval first, so it replaced `terraform refresh`.
- After a refresh-only apply, a normal `plan` may still show changes. Your configuration still differs from the now-updated state. For example, if someone changed a tag in the console, a refresh-only apply records the new tag in state. The next `plan` will then propose reverting it to match your code, unless you update the code to match.
- `terraform plan -refresh-only` also exists. It is the preview-only version, showing drift without writing state.

| | `plan` | `apply -refresh-only` |
|---|---|---|
| Compares | Config vs. refreshed state | Real infrastructure vs. state |
| Changes infrastructure | No | No |
| Changes state | No | Yes, after approval |
| Typical purpose | Preview changes | Accept drift into state |

One security note: state can contain secrets. A refresh-only apply writes fresh values from the provider into it, so make sure your backend is encrypted and access-controlled.
