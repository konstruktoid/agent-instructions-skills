I haven't changed anything, because I couldn't find the code you described anywhere in this workspace.

- **No role writes AWS credentials.** The only Ansible role is `roles/nginx`. Its tasks (`roles/nginx/tasks/main.yml:1-11`) install nginx and render a site config. Its defaults hold only `nginx_worker_processes`.
- **No credentials anywhere in the repo.** I searched every file for `aws`, `credential` and `secret`, case-insensitive. The only hit was `infra/main.tf:1`, an `aws_security_group "bastion"` resource.
- **No build host in the Terraform.** `infra/main.tf` doesn't define an EC2 instance, IAM role or instance profile, so there's nothing to attach a profile to yet.

Moving to an instance profile would mean these changes:

1. **Terraform:** add an IAM role whose trust policy lets EC2 assume it, a policy limited to the permissions the build actually needs, and an `aws_iam_instance_profile` attached to the build host's instance.
2. **Ansible:** remove the task that writes `~/.aws/credentials` and the variables that feed it. Add a task that deletes any credentials file already on the host, so a stale file doesn't take priority over the profile.
3. **Clean up the old keys:** rotate or deactivate the IAM user's access keys and remove them from wherever the role pulled them, such as vault files or CI variables.

To do this I need one of the following:

- The right repo or branch, if the credentials role and build host live somewhere else.
- The role's path, if it's in a directory I haven't seen.
- Confirmation that you want me to write it from scratch here. In that case, tell me which AWS actions the build needs, plus the build host's AMI, subnet and instance type, or whether it's managed outside Terraform.

Separately, `infra/main.tf` opens SSH (port 22) on the bastion to `0.0.0.0/0`, meaning the whole internet. You may want to restrict that while we're in this file.
