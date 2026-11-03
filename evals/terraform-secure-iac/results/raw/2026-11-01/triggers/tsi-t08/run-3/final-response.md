I couldn't find a CloudFormation template in this workspace. Nothing contains `AWSTemplateFormatVersion`, `AWS::` resource types or a `Parameters:` block. The YAML files here are a GitHub Actions workflow, a GitLab CI file, docker-compose, a Kubernetes deployment and an Ansible nginx role.

Can you paste the template or give me its path? Once I have it, I'll convert each parameter to the right SSM type:

- **Plain config values** (AMI IDs, VPC/subnet IDs, instance types, etc.) become typed SSM parameters, e.g. `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>`, `AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>`, `AWS::SSM::Parameter::Value<List<AWS::EC2::Subnet::Id>>` or `AWS::SSM::Parameter::Value<String>`. The `Default` becomes the SSM parameter name, such as `/myapp/prod/vpc-id`.
- **Secrets** (passwords, API keys) are a special case. CloudFormation parameter types can't read `SecureString` parameters. For those I'd switch to a `{{resolve:ssm-secure:/path}}` or `{{resolve:secretsmanager:...}}` dynamic reference where the value is used. That keeps the secret out of the template and out of the stack's parameter history. Leaving them as `NoEcho` String parameters is the other option.

If you'd like to see the pattern first, I can write a small example template instead.
