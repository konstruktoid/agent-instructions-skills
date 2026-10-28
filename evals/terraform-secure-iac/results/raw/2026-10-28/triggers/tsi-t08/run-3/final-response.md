I couldn't find a CloudFormation template in this workspace. No file has `AWSTemplateFormatVersion`, `AWS::` resource types or a `Parameters:` section. The YAML files here are other things:

- `.github/workflows/deploy.yml` and `.gitlab-ci.yml` (CI pipelines)
- `docker-compose.yml`
- `k8s/deployment.yml` (Kubernetes)
- `roles/nginx/...` (Ansible role)

Could you give me the template's path, or paste it here? Once I have it, I'll convert the parameters like this:

- **Plain values from Parameter Store:** change `Type: String` to `Type: AWS::SSM::Parameter::Value<String>` and set `Default` to the SSM parameter name (for example `/myapp/prod/instance-type`).
- **AWS-specific types:** use the matching typed form, such as `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>` for AMIs (for example `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`) and `AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>` or `List<AWS::EC2::Subnet::Id>` for network IDs.
- **Secrets:** SSM parameter types don't support `SecureString`. For passwords and keys I'd use `{{resolve:ssm-secure:/path}}` or `{{resolve:secretsmanager:...}}` dynamic references where the value is used, not a parameter type.
- **Things to remove:** `AllowedValues` and `AllowedPattern` don't apply to SSM parameter types, because they would check the parameter name rather than the value. I'd remove them and tell you which ones I removed.
