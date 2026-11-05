I couldn't find anything in this repo that writes AWS credentials, so I haven't changed anything.

- The only Ansible role is `roles/nginx`. It installs nginx and templates `site.conf`, and it doesn't touch `~/.aws/credentials`.
- A case-insensitive search of every file for `credential`, `AWS_`, `.aws`, `boto` and `aws_access_key` found nothing. That includes the CI files, `docker-compose.yml` and `k8s/deployment.yml`.
- `infra/main.tf` has only a bastion security group. It has no IAM role, instance profile or EC2 instance.

The role you mean is probably in another repo, or on a different branch or in a different checkout. Can you point me to it?

Once I can see it, the change would have three parts:

1. **Remove the credentials write.** Delete the tasks that write `~/.aws/credentials`, along with the key variables and any vaulted values that feed them. The old keys should then be rotated or deleted in IAM, because they're already on disk and possibly in git history.
2. **Add the instance profile in Terraform.** This means an `aws_iam_role` that trusts `ec2.amazonaws.com`, a least-privilege policy limited to what the build actually calls, and an `aws_iam_instance_profile`. The profile gets attached to the build host through `iam_instance_profile`.
3. **Harden the instance metadata service.** Require IMDSv2 (`http_tokens = "required"`) and use a small hop limit.

I'd also need to know how the build host is created: Terraform, the console, or something else. That decides where the profile gets attached.
