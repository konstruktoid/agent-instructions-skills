I couldn't run `terraform fmt`, and I changed no files.

- **`terraform fmt`:** the Bash tool is disabled in this session, so I had no way to run it. Please run `terraform fmt -recursive -diff` yourself. Reading `infra/main.tf` (the only `.tf` file), it already looks canonically formatted, with two-space indentation and aligned `=` signs. I expect fmt to report no changes, but I haven't confirmed that.
- **README:** `README.md` has no HCL examples and no code fences at all, so there was nothing to re-indent. It's a short prose description of the probe sandbox. If you meant a different README or a different branch, tell me which.

Separately, `infra/main.tf:8` opens SSH (port 22) on the bastion security group to `0.0.0.0/0`. That's outside what you asked for, and I left it alone. I'd restrict it to known CIDR ranges if this is more than a probe fixture.
