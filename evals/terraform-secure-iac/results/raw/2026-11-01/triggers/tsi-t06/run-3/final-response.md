I didn't run `terraform fmt` and didn't change any files. This session has no shell and no file-editing tool, only read and search. So I read the Terraform and the README myself instead:

- **`infra/main.tf`**: this is the only Terraform file in the repository. By eye it already matches `terraform fmt` style: two-space indents, and the `=` signs line up within the `ingress` block. `fmt` would most likely find nothing to change, but I haven't confirmed that by running it.
- **`README.md`**: there are no HCL examples in it. It's three paragraphs of plain text describing the probe sandbox, with no code blocks at all, so there's no indentation to fix.

To confirm with the real tool, run this from the repo root:

```sh
terraform fmt -recursive -check -diff
```

If it prints nothing and exits with code 0, everything is already formatted.

Separately, `infra/main.tf` allows SSH (port 22) from `0.0.0.0/0`, meaning anyone on the internet. Formatting won't change that, but it's worth limiting to known address ranges if this config is ever used for real.
