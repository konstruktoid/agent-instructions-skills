I couldn't find a CloudFormation template in this workspace, so I haven't changed anything. I searched for `AWSTemplateFormatVersion`, `AWS::` resource types and `Parameters:` blocks. The only YAML here is:

- `.github/workflows/deploy.yml` (GitHub Actions)
- `docker-compose.yml`
- `k8s/deployment.yml` (Kubernetes)
- `.gitlab-ci.yml`
- `roles/nginx/...` (Ansible)

None of these has a CloudFormation `Parameters` section.

Could you give me the template's path or paste it here? Once I have it, I'll convert parameters like this:

- **AMI IDs** → `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>`, with the default set to a public path such as `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`
- **Plain strings and lists** → `AWS::SSM::Parameter::Value<String>` or `AWS::SSM::Parameter::Value<List<String>>`
- **VPC, subnet and security group IDs** → `AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>` and the other `AWS::EC2::*` types
- **Secrets (passwords, tokens)**: SSM parameter types can't read `SecureString` values. For these I'd use a dynamic reference instead (`{{resolve:ssm-secure:...}}` or `{{resolve:secretsmanager:...}}`) and leave out `NoEcho` defaults.

If you meant the GitHub Actions or Kubernetes file instead, tell me and I'll work on that.
