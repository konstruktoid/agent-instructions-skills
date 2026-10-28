I couldn't run `terraform fmt`, and I didn't change anything. This session has no shell or file-editing tools, only read and search. I read the files by hand instead.

- **`infra/main.tf`** (the only Terraform file) already looks like `terraform fmt` output: two-space indentation and aligned `=` signs inside the `ingress` block. I'd expect no changes from fmt, but that's from reading it, not from running it.
- **`README.md`** has no HCL examples or code blocks of any kind. It's four paragraphs describing this probe-sandbox repository, so there's no indentation to fix there.

To confirm the formatting, run this from the repo root:

```sh
terraform fmt -recursive -check -diff
```

If it prints nothing and exits with code 0, everything is already formatted.

`main.tf` also allows SSH (port 22) from `0.0.0.0/0`, meaning the whole internet. That's a security issue rather than a formatting one, so I left it alone. I can review it if you want.
