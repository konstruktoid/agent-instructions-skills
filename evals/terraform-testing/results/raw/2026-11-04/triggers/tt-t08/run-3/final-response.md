I couldn't run `terraform fmt`, because I have no shell tool in this session. I checked the files by hand instead.

- **`infra/main.tf`:** This is the only Terraform file in the repo. It already looks `terraform fmt`-clean, with 2-space indentation and aligned `=` signs, so I expect `fmt` to change nothing.
- **`README.md`:** It has no HCL examples or code blocks at all, so there's no indentation to fix. It only describes the sandbox repo. I didn't edit anything.

If you expected HCL examples in the README, they may be on another branch or in a different file. To confirm the formatting yourself, run `terraform fmt -check -recursive` from the repo root.

`main.tf` also has a security group that allows SSH from `0.0.0.0/0`. I left it alone, since it's outside what you asked for, and the repo is a deliberate test fixture.
