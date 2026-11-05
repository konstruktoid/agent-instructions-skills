I couldn't find the Ansible role that writes AWS credentials, so I haven't changed anything.

- **Ansible:** the only role here is `roles/nginx`. It installs nginx and renders `site.conf`. Nothing in it touches `~/.aws/credentials`, `aws_access_key`, or `aws_secret`.
- **Rest of the repo:** a case-insensitive search for `credential`, `AWS_`, `.aws`, `instance_profile` and `iam` matched nothing except the word "bastion" in `infra/main.tf` (an `iam` substring hit). That file holds one security group, with no IAM role or instance profile. The CI files (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`) also had no matches.

The role is probably in another repository, or on a branch or path that isn't checked out here. Can you point me to it?

Once I can see it, the change would normally be in three parts:
1. **Terraform:** add an `aws_iam_role` with an EC2 trust policy, scope its permissions to what the build needs, and add an `aws_iam_instance_profile`. Attach the profile to the build host's `aws_instance` or launch template.
2. **Ansible:** delete the tasks that write `~/.aws/credentials`, along with their variables and vault entries. The AWS CLI and SDKs pick up instance-profile credentials from the metadata service on their own.
3. **Cleanup:** deactivate and rotate the old IAM user's access keys. They've been on disk and possibly in vars or vault, so treat them as exposed. Also require IMDSv2 (`http_tokens = "required"`) on the host.

I haven't looked at what the build host is or what it needs to reach, so the role's permissions are still to be decided.
