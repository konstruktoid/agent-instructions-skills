I couldn't find the credentials task, so I haven't changed anything.

I searched the whole workspace for `aws`, `credentials`, `access_key` and `secret`, and nothing in it writes `~/.aws/credentials`:

- **`roles/nginx/`** is the only Ansible role. Its tasks install nginx and render `/etc/nginx/conf.d/site.conf`, and its defaults set only `nginx_worker_processes`.
- **`infra/main.tf`** has a single `aws_security_group` (`bastion`). There's no EC2 instance, IAM role or instance profile.
- No other file mentions AWS at all, including `inventory.ini`, the CI files, `Dockerfile` and `scripts/backup.sh`.

The role you mean is probably in another repo, branch or Ansible collection that isn't checked out here.

To make the change I'd need:

1. **Where the role is.** A path, repo or branch I can open.
2. **Where the build host runs.** An instance profile only works on EC2. If the host is on-prem or a CI runner outside AWS, the usual way to remove static keys is something else: IAM Roles Anywhere, GitHub/GitLab OIDC federation, or SSO.
3. **What the credentials are used for.** I need the actions and resources to write a least-privilege policy rather than copy whatever the current keys allow.
4. **Who owns the EC2 instance.** If Terraform manages it, I'd add the IAM role, the policy, the `aws_iam_instance_profile` and the `iam_instance_profile` setting on the instance. I'd also delete the Ansible task, add a task to remove the existing `~/.aws/credentials` file, and suggest deactivating the old access keys.

Separately, `infra/main.tf:8` opens SSH (port 22) on the `bastion` security group to `0.0.0.0/0`. That's worth narrowing whatever happens with the credentials.
