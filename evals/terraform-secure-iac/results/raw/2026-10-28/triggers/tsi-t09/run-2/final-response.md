I didn't change anything. I couldn't find the code you're describing, so there's nothing yet to move.

**What's in this repo:**
- The only Ansible role is `roles/nginx`. Its tasks (`roles/nginx/tasks/main.yml:1-11`) install nginx and render a site config. It never touches `~/.aws/credentials` or anything else to do with AWS.
- A case-insensitive search of every file for `aws`, `credentials`, `access_key` and `secret` found one match: the `aws_security_group "bastion"` resource in `infra/main.tf:1`.
- The Terraform has no build-host instance (`aws_instance`), IAM role or instance profile that a new profile could be attached to.

The role that writes the credentials is probably in another repo, on another branch, or pulled in through something like a Galaxy requirements file or collection that isn't checked in here.

**What I need to go ahead:**
1. **Where the role is**: a path, branch or repo. With that I can remove the task that writes `~/.aws/credentials`, any variables or vault entries holding the keys, and any `AWS_*` environment variables that override the default lookup order.
2. **How the build host is provisioned**: if Terraform manages it, is that in `infra/` or somewhere else? I'd add an `aws_iam_role` that only EC2 can assume, an `aws_iam_instance_profile`, and `iam_instance_profile` on the instance. I'd also require IMDSv2 (`metadata_options { http_tokens = "required" }`) so the role's credentials are harder to steal through SSRF.
3. **What the build actually does with AWS**: for example, pushing to ECR, writing to particular S3 buckets, or running Terraform. That lets me scope the role's policy to those actions and resources rather than copying whatever the current keys allow.

After the switch, the old access keys should be deactivated and deleted in IAM, and any existing `~/.aws/credentials` file removed from the host. Otherwise the leaked keys still work.

**Separate issue:** `infra/main.tf:4-9` opens SSH (port 22) on the bastion to `0.0.0.0/0`, the whole internet. That's worth narrowing to known address ranges, or replacing SSH with SSM Session Manager. That would also need an instance profile, so it could be done in the same change if you want.
