I didn't change anything. I couldn't run `terraform fmt`, and I found no HCL examples in the README to fix.

- **`terraform fmt`:** This session has no shell tool, so I couldn't run it. I read the repository's only `.tf` file, `infra/main.tf`, and it looks correctly formatted: two-space indentation and aligned `=` signs. You can confirm with `terraform fmt -recursive -check -diff`.
- **README:** `README.md` has no code blocks at all. It's a short description of the trigger-eval sandbox. If you meant a different README, tell me which one.

**Security issue in `infra/main.tf`:** The `bastion` security group allows SSH (port 22) from `0.0.0.0/0`, which is open to the whole internet. I didn't touch it because it's outside what you asked for. I can restrict it to a specific CIDR range if you give me one.
