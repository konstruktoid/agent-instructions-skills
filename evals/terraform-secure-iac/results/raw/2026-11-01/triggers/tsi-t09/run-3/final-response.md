I couldn't find the code you described, so I haven't changed anything.

**What I searched:**
- `roles/` has only one role, `roles/nginx`. Its tasks install nginx and render `site.conf.j2`. Nothing in it writes to `~/.aws/credentials`.
- Across the whole workspace, a search for `aws`, `credential`, `access_key`, `secret_access` and `instance_profile` found one hit: `infra/main.tf:1`, a bastion security group. No IAM role or instance profile exists, and no EC2 instance is defined for one to attach to.
- `inventory.ini` lists only `web` and `db` hosts. There's no build host group.

So the role you mean is probably in another repo, on another branch, or pulled in from somewhere else (Galaxy, a submodule). I didn't want to guess and add an IAM role and instance profile without knowing who uses the credentials or what they need to reach.

**To go ahead, I need:**
1. Where that role and its credentials task are.
2. What the build host does with the credentials (S3 buckets, ECR, etc.), so the IAM policy grants only what's needed.
3. Whether the build host's EC2 instance is managed in this repo's Terraform or somewhere else.

Once I have those, the plan is:
- Add an IAM role that only EC2 can assume, with a narrowly scoped policy, plus an `aws_iam_instance_profile`, and attach it to the build instance.
- Require IMDSv2 on that instance (`http_tokens = "required"`).
- Remove the credentials task and any variables or vault entries that hold the keys. Add a task to delete the existing `~/.aws/credentials` from the build host.
- Deactivate and delete the old access keys in IAM. Deleting the file alone doesn't stop them working anywhere they've already been copied.

Separately, `infra/main.tf` opens SSH (port 22) on the bastion to `0.0.0.0/0`, which means anyone on the internet. You may want to restrict that too.
