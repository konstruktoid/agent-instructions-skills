I didn't run `terraform fmt` because I don't have a shell in this session. There was also nothing in the README to fix.

- **README:** `README.md` has no HCL examples, or code blocks of any kind. It's a short prose description of the sandbox repo, so there's no indentation to correct.
- **Terraform:** `infra/main.tf` is the only `.tf` file in the repo. I read it by hand and it already looks like `terraform fmt` output: two-space indentation, and the `=` signs line up in the `ingress` block. I haven't confirmed that with the tool. You can check with `terraform fmt -check -recursive`, which exits 0 if nothing needs changing.

Separately, `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0` on the bastion security group, which lets anyone on the internet reach it. If this config is meant to be used for real, you should narrow that range. I left it alone because you only asked for formatting.

If the HCL examples you meant are in a different README or another branch, tell me where and I'll look there.
