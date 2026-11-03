I couldn't make the change. Nothing in this repository writes AWS credentials, and nothing defines the build host, so there's nothing yet to move to an instance profile.

What I found:

- **`roles/nginx/`** is the only Ansible role here. Its tasks (`roles/nginx/tasks/main.yml`) only install nginx and render `site.conf`. Its defaults only set `nginx_worker_processes`. It has no task touching `~/.aws/credentials`.
- **A search of the whole workspace** for `aws`, `credential`, `access_key` and `instance_profile` found only one match: `infra/main.tf:1`.
- **`infra/main.tf`** defines only one security group, `bastion`. There's no EC2 instance, IAM role or instance profile for the build host, so I'd have nothing to attach a profile to.

Also, I have no file-editing tools in this session, so even with the right files I could only describe the change, not apply it.

To go further, I need:

1. **The role that writes the credentials.** It may be in another repository or a Galaxy collection. A path or the task itself is enough.
2. **Where the build host is created.** Is it in Terraform elsewhere, made by hand, or not on EC2 at all? An instance profile only works on EC2.
3. **What AWS access the build host needs**, such as S3 buckets or ECR repositories. That lets me scope the role's permissions to just that instead of copying whatever the current static keys allow.

Once I have those, the change would be:

- **In Terraform:** add an IAM role that EC2 can assume, a least-privilege policy, and an `aws_iam_instance_profile` attached to the build host. Also require IMDSv2 on the instance (`http_tokens = "required"`) so the profile's credentials are harder to steal.
- **In Ansible:** remove the task that writes the credentials, and add one that deletes the existing `~/.aws/credentials` file (`state: absent`).
- **In AWS:** deactivate and delete the old access keys once the profile works, since they may already be exposed.

Separately, `infra/main.tf` allows SSH (port 22) from `0.0.0.0/0` on the `bastion` group, which you probably want narrowed.
