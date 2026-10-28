I couldn't find a CloudFormation template in this workspace. I searched every YAML/JSON file and grepped for `AWSTemplateFormatVersion` and `Parameters:`, and nothing matched. The workspace only has these files:

- `.github/workflows/deploy.yml`
- `.gitlab-ci.yml`
- `docker-compose.yml`
- `k8s/deployment.yml`
- `roles/nginx/...` (Ansible role)

None of these are CloudFormation. Could you paste the template or give me its path? Once I have it, I'll convert the parameters, roughly like this:

```yaml
Parameters:
  # Before: Type: String, Default: ami-0abc123...
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64

  # Before: Type: String
  VpcId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>
    Default: /myapp/prod/vpc-id

  SubnetIds:
    Type: AWS::SSM::Parameter::Value<List<AWS::EC2::Subnet::Id>>
    Default: /myapp/prod/subnet-ids
```

When I convert yours, I'll handle these limits of SSM parameter types:

- **SecureString isn't supported** as an SSM parameter type. Secrets like passwords need a dynamic reference instead: `{{resolve:ssm-secure:/path}}` (only some resource properties accept it) or `{{resolve:secretsmanager:...}}`. They shouldn't become plain `String` parameters with `NoEcho`.
- **Values are read when the stack is created or updated, not continuously.** If the SSM value changes, the stack only picks it up on the next update.
- **The SSM parameters must already exist** in the target account and region before you deploy. I'll list each one the template will expect.
