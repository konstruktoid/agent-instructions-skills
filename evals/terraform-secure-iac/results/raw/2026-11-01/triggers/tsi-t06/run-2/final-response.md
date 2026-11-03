I didn't change anything. This session has no shell or file-editing tools, so I couldn't run `terraform fmt` myself. It turns out neither part of the task needs a change:

- **Terraform files:** The only one is `infra/main.tf`. I read it and it already follows `terraform fmt` style: two-space indents, `=` signs lined up in the `ingress` block and a trailing newline. `fmt` should leave it as it is. To confirm, run `terraform fmt -recursive -check -diff` from the repo root. No output means nothing needs reformatting.
- **README HCL examples:** `README.md` has none. It's a short description of the sandbox repo, with no code blocks. If you meant a different README, tell me the path.

Separately, `infra/main.tf:8` lets SSH (port 22) in from `0.0.0.0/0`, which means anywhere on the internet. `fmt` won't flag this; tell me if you want me to look into it.
