Done. Changes made:

- **`.github/workflows/deploy.yml`**: added `tags: ['v*']` trigger alongside `push: main`; replaced `permissions: write-all` with least-privilege `id-token: write` + `contents: read` (the `id-token` grant is what actually enables OIDC); swapped the static `aws-access-key-id`/`aws-secret-access-key` for `role-to-assume: arn:aws:iam::123456789012:role/deploy-widget`, keeping `aws-region: eu-north-1`. The Slack notify step and `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` secrets weren't referenced elsewhere, so nothing else needed touching — the Slack step is untouched.
- **`README.md`**: documented the new trigger conditions and the OIDC role-assumption auth (no more long-lived keys), noting the repo remains public.

Note: I left the AWS secrets (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`) in the repo's GitHub secrets store as-is — you'll want to delete those from the repo settings and deregister/rotate the IAM user's keys on the AWS side once this is confirmed working, since removing them from the workflow doesn't revoke them.
