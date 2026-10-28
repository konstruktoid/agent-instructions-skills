I didn't change anything. Neither part of the request needed a change, though I couldn't actually run `terraform fmt`.

- **`terraform fmt`:** I have no shell in this session, so I couldn't run it. I checked the only Terraform file by eye instead. `infra/main.tf` already looks like what `fmt` would produce: two-space indentation, and the `=` signs in the `ingress` block lined up. Run `terraform fmt -recursive -check` yourself to confirm; if it prints no file names, nothing needs formatting.
- **README HCL examples:** `README.md` doesn't contain any. It's a short prose description of the probe-sandbox repo with no code blocks, so there was no indentation to fix. If you meant a different README, tell me which one.

Separately, `infra/main.tf` allows SSH (port 22) in from `0.0.0.0/0`, meaning anywhere on the internet. I didn't change it because it's outside this task, and the README says the repo is test material, so it may be intentional.
