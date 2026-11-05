I couldn't find anything to migrate, so I haven't changed any files.

- **No credentials are written anywhere.** The only Ansible role in this workspace is `roles/nginx`. It installs nginx and templates `/etc/nginx/conf.d/site.conf`, and it never touches `~/.aws/credentials`.
- **Nothing else mentions AWS credentials.** A case-insensitive search of the whole repo for `aws`, `credential` and `AKIA` found one hit. That was the `aws_security_group.bastion` resource in `infra/main.tf`. The CI files (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`), `docker-compose.yml` and `k8s/deployment.yml` have no matches.
- **There is no build-host instance to attach a profile to.** `infra/main.tf` has only that security group, with no `aws_instance`, launch template or IAM resources.

The role may live in another repo, or this may be the wrong branch or checkout. If you point me to the right one, I'll do the migration there:

1. Remove the task that writes `~/.aws/credentials`, along with the secret variables or vault entries that feed it.
2. Add an IAM role, an `aws_iam_instance_profile`, and a least-privilege policy to the Terraform. Attach the profile to the build host's instance or launch template.
3. Require IMDSv2 on the instance. The AWS SDK and CLI then pick up the role credentials without any file on disk.
4. Rotate the old access key, since it has been sitting on disk and probably in the repo or vault.

Separately, `infra/main.tf` allows SSH from `0.0.0.0/0` on the bastion security group. I left it alone because you didn't ask about it, but I can tighten it if you want.
