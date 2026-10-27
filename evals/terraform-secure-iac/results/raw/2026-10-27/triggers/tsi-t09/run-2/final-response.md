I couldn't find the code you described, so I haven't changed anything.

**What I searched:**
- `roles/` has only an `nginx` role. Its tasks install nginx and render `site.conf`. Its defaults set only `nginx_worker_processes`. Nothing in it touches `~/.aws/credentials`.
- I searched the whole repo for `aws`, `credentials`, `access_key` and `secret`. The only match is `infra/main.tf:1`, a bastion security group.
- No Terraform here defines the build host: there's no `aws_instance`, launch template, IAM role or instance profile.

So nothing in this repo writes the credentials file, and nothing defines an instance I could attach a profile to.

**Possible explanations:**
1. The role lives in a different repo, or on a branch that isn't checked out here.
2. The credentials are written by something outside the role, such as the CI config, a Jenkins stage or a `user_data` script. I can check `Jenkinsfile`, `.gitlab-ci.yml` and `.github/workflows/deploy.yml` next if you think that's likely.
3. The build host is managed outside this repo's Terraform.

**What the fix will need once I find it:**
- **Terraform:** an `aws_iam_role` with an EC2 trust policy, a policy limited to what the build actually calls, an `aws_iam_instance_profile`, and `iam_instance_profile` set on the build host's instance or launch template. Also `http_tokens = "required"` (IMDSv2), so the role's credentials can't be pulled through a simple server-side request forgery.
- **Ansible:** remove the task that writes the credentials file and the variables that hold the keys. Add a task that deletes the existing `~/.aws/credentials` from the build host. The AWS SDK and CLI will then pick up the instance profile without any extra setup.
- **Outside the code:** once nothing uses the old access key, deactivate and delete it in IAM. Assume it's been exposed, since it was sitting on disk and probably in Ansible vars.

Can you tell me where the role and the build host's infrastructure live? Or should I check the CI files first?
