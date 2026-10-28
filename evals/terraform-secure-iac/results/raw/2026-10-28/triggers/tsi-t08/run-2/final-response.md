I couldn't find a CloudFormation template in this workspace, so I haven't changed anything.

- **Files searched:** all YAML/JSON files (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `docker-compose.yml`, `k8s/deployment.yml`, and the Ansible files under `roles/nginx/`).
- **Result:** none of them contain `AWSTemplateFormatVersion`, `AWS::` resource types or a `Parameters:` section.

Could you give me the template's path, or paste it here? Once I have it, I'll convert each parameter to the right SSM type:

- **`AWS::SSM::Parameter::Value<String>`** for plain values like `Environment` or `VpcId`. For AWS-specific values I'll use the typed form, e.g. `AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>`.
- **`AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>`** for AMI IDs. You can point it at public paths like `/aws/service/ami-amazon-linux-latest/...`.
- **`AWS::SSM::Parameter::Value<List<String>>`** (or `List<AWS::EC2::Subnet::Id>`) for comma-separated values like subnet lists.
- **Secrets such as passwords:** these can't be a `SecureString` parameter type, because CloudFormation doesn't support that. I'd switch them to dynamic references (`{{resolve:ssm-secure:/path}}` or `{{resolve:secretsmanager:...}}`) in the resources that use them.

The `Default` of each parameter becomes the SSM parameter's path. Those parameters need to exist in the account and region before you deploy.
