I couldn't find the credential-writing code in this repo, so I haven't changed anything.

- A case-insensitive search for `aws/credentials`, `aws_access_key` and `aws_secret` found no matches anywhere.
- The only Ansible role here is `roles/nginx`. It installs nginx and renders `site.conf`, and it never touches `~/.aws`.
- `infra/main.tf` has a single security group and no instance, IAM role or instance profile.

The role you mean may live in another repo or branch. It could also be in a file I didn't search, such as the CI configs (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`), which my search did cover for those strings.

Once you point me to the role, the change would normally have two parts:

1. **Terraform:**
   - Add an `aws_iam_role` with an EC2 trust policy.
   - Attach a least-privilege policy for only what the build needs.
   - Add an `aws_iam_instance_profile`, and reference it from the build host's `iam_instance_profile`.
   - Require IMDSv2 with `metadata_options { http_tokens = "required" }`.
2. **Ansible:**
   - Remove the task that writes `~/.aws/credentials`, along with its key variables and vault entries.
   - Add a task that deletes the existing file on hosts that already have it.
   - Rotate the old access keys, because they have already been on disk.

Where is the role, and which AWS actions does the build host need? I need the actions to scope the policy.

I also noticed that `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion. That's outside what you asked for, so I left it alone.
