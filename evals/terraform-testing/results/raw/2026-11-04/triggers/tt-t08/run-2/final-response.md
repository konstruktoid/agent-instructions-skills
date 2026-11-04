I couldn't run `terraform fmt`, and I changed no files. This session has no shell tool and no file-editing tool. I can only read and search files, so I can't run commands or write changes.

Here is what I found by reading the files:
- **`infra/main.tf`:** It's already formatted the way `terraform fmt` would leave it. It uses two-space indentation and aligned `=` signs, so the command should change nothing.
- **`README.md`:** It has no HCL code blocks, so there's no indentation to fix. It's only prose.
- **Other files:** The only `.tf` and `.md` files in the repo are those two.

To confirm, run `terraform fmt -recursive -check -diff` from the repo root. If you meant a different README, or the HCL examples are on another branch, tell me which and I'll look there.
