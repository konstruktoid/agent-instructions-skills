I couldn't find a CloudFormation template in this workspace. I searched every YAML/JSON file and grepped for `AWSTemplateFormatVersion`, `AWS::` and `Parameters:`, and nothing matched. The only files here are a GitHub Actions workflow, `.gitlab-ci.yml`, `docker-compose.yml`, a Kubernetes manifest and an Ansible nginx role.

Can you give me the template's path, or paste it here? Once I have it, I'll convert the parameters. Here's what the change looks like:

```yaml
# Before
Parameters:
  ImageId:
    Type: AWS::EC2::Image::Id
    Default: ami-0abc123
  VpcId:
    Type: String

# After
Parameters:
  ImageId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64
  VpcId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>
    Default: /myapp/network/vpc-id
```

There are a few things to keep in mind:
- **Secrets can't use these types.** `AWS::SSM::Parameter::Value<...>` doesn't support `SecureString`. Passwords and keys need a dynamic reference in the resource instead, such as `{{resolve:ssm-secure:/path}}` or `{{resolve:secretsmanager:...}}`. Parameters that currently use `NoEcho` fall into this group.
- **Defaults change meaning.** A default becomes the SSM parameter's name, not the value itself. Each parameter also needs to exist in SSM before you deploy.
- **Values are read at deploy time.** CloudFormation reads them when the stack is created or updated. If you change a value in SSM, the stack won't pick it up until its next update.
