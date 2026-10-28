I couldn't find the code you described, so I haven't changed anything.

**What's in this workspace:**
- **`roles/nginx` is the only Ansible role.** Its tasks (`roles/nginx/tasks/main.yml:1-11`) install nginx and render `/etc/nginx/conf.d/site.conf`. Nothing writes to `~/.aws/credentials`.
- **Nothing else mentions AWS credentials.** I searched every file for `aws`, `credential` and `secret`. The only match is `infra/main.tf:1`, a security group, and nothing there sets up IAM or an instance profile.

The role you mean is probably in another repo, a Galaxy or collection dependency, or a branch that isn't checked out here. Also, this session only gives me tools to read and search files, so I couldn't edit them even once we find the right code.

**What the change would involve once I can see it:**
1. **Terraform:** create an `aws_iam_role` with an `ec2.amazonaws.com` trust policy and a policy limited to the actions the build actually needs. Wrap it in an `aws_iam_instance_profile` and attach that to the build host's `aws_instance` (or launch template). Also require IMDSv2 on the instance (`metadata_options { http_tokens = "required" }`).
2. **Ansible:** remove the task that renders `~/.aws/credentials`. Add a task that deletes any existing file (`ansible.builtin.file: state=absent`), and remove the access-key variables from vars and vault. The AWS SDK and CLI will then get credentials from the instance profile automatically.
3. **Rotation:** deactivate and delete the old IAM user's access keys once the build host works with the role. Those keys have been on disk, so treat them as exposed.

To go ahead, point me to the role that writes the credentials and the Terraform that creates the build host, and run me with edit access.
