YAML is valid; no remaining references to the static credential secrets.

Changed: `.github/workflows/deploy.yml`, `README.md`.

Two things outside this task's scope worth flagging:
- README says "This repository is public" — the IAM role's trust policy must restrict `sub` to this exact repo/ref (branch `main` and your `v*` tags), otherwise any public fork or PR workflow could attempt to assume it. That's configured on the AWS side, not in this file.
- The runner is `self-hosted` on what you've stated is a public repo — a known-risky combination since PRs from forks can run arbitrary code on it. Separate issue, not touched here.

Not committing — say the word if you want these staged.
