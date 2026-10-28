I couldn't find any code in this repo that writes AWS credentials, so I haven't changed anything.

What I checked:

- **The only Ansible role is `roles/nginx`.** Its `tasks/main.yml` just installs nginx and renders `site.conf`. Its `defaults/main.yml` only sets `nginx_worker_processes`, and it has a `handlers/main.yml` as well. Nothing touches `~/.aws/credentials`.
- **I searched the whole repo for `aws`, `credentials`, `access_key` and `secret` (case-insensitive).** The only match was `infra/main.tf:1`, a `bastion` security group.
- **`infra/main.tf` doesn't define the build host.** There's no instance, launch template, IAM role or instance profile, so there's nothing yet to attach a profile to.

So the role you mean probably lives somewhere else: another repo, a Galaxy or collection role, or a CI variable that `inventory.ini`, the `Jenkinsfile` or the pipelines feed into Ansible.

To do the migration, please point me to:

1. **The role or task that writes `~/.aws/credentials`**, so I can remove it, delete the file and its vars, and stop sourcing the secret.
2. **Where the build host is provisioned**, so I can add an IAM role, trust policy and `aws_iam_instance_profile` there and attach it to the instance.
3. **What the build host actually does with those credentials.** Things like S3 buckets, ECR pushes or a specific deploy role tell me what permissions to grant. That way the role is limited to that, rather than copying whatever the current key allows.

Once the profile is live, the key behind the old credentials file should be deactivated and deleted in IAM. It has been sitting in plain text on the host and in Ansible vars, so treat it as exposed.

Separately, `infra/main.tf` opens SSH (port 22) to `0.0.0.0/0` on the bastion. That isn't part of this task, but you may want to restrict it.
