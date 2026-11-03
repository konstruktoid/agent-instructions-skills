I didn't change anything, because nothing in this workspace writes AWS credentials.

- **Ansible:** the only role is `roles/nginx`. Its tasks (`roles/nginx/tasks/main.yml:1`) install nginx and render `site.conf`. Nothing touches `~/.aws/credentials`.
- **Whole repo:** I searched every file for `aws`, `credential`, `access_key` and `secret`. The only hit is `infra/main.tf:1`, a security group resource. There are no credentials, IAM resources or instance profiles anywhere.

So the role you mean is probably in another repo or branch. Can you point me to it, or to the role and task name?

Once I have it, the plan is:

1. **Terraform** (`infra/`): add an IAM role with an EC2 trust policy and a narrowly scoped policy that grants only the AWS actions the build actually needs. Then add an `aws_iam_instance_profile` and attach it to the build host's `aws_instance` through `iam_instance_profile`. I'd also require IMDSv2 (`metadata_options { http_tokens = "required" }`) so the role's credentials are harder to steal from the instance. I'll check the result with your repo's fmt, validate, tflint and scanner, if those are set up.
2. **Ansible:** delete the task that writes `~/.aws/credentials` and the variables or vault entries behind it. Add a task that removes the existing file from build hosts, since it isn't deleted automatically.
3. **Afterwards:** deactivate and delete the IAM user's access keys. Removing them from config doesn't revoke them, and they've been sitting on disk.

Separately, `infra/main.tf:4-9` opens SSH (port 22) to `0.0.0.0/0`, meaning the whole internet. I left it alone because it's out of scope, but you probably want to restrict it.
