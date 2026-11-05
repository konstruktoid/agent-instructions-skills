I couldn't find a CloudFormation template in the workspace, so I haven't changed anything. A search for `AWSTemplateFormatVersion` and `AWS::CloudFormation` matched no files. The only YAML files here are CI workflows, `docker-compose.yml`, `k8s/deployment.yml` and the nginx Ansible role.

Please paste the template or give me its path, and I'll convert the `Parameters` section.

In the meantime, this is what the conversion usually involves:

- **Type change:** `Type: String` becomes `Type: AWS::SSM::Parameter::Value<String>`. Other options are `AWS::SSM::Parameter::Value<List<String>>` and `AWS::SSM::Parameter::Value<CommaDelimitedList>`. For AWS resource IDs you can use `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>`, which also validates the value.
- **What the parameter holds:** the `Default` (or the value passed at deploy time) is now the SSM parameter name, such as `/app/prod/vpc-id`. It is no longer the value itself.
- **Secrets:** CloudFormation can't resolve `SecureString` parameters through SSM parameter types. For secrets, use a dynamic reference like `{{resolve:ssm-secure:/path:version}}` in the resource properties, or Secrets Manager. Tell me which parameters are secrets.
- **Permissions:** the deploying role needs `ssm:GetParameters` on the parameter paths.
