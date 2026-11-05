I couldn't find a CloudFormation template in the workspace, so I haven't changed anything. The only YAML files here are `.github/workflows/deploy.yml`, `.gitlab-ci.yml`, `docker-compose.yml`, `k8s/deployment.yml` and the `roles/nginx/*` Ansible files. A search for `AWSTemplateFormatVersion`, `AWS::CloudFormation` and `Parameters:` matched nothing.

Please paste the template or give me its path.

When you send it, I'll convert the parameters like this:
- **Type:** `String` becomes `AWS::SSM::Parameter::Value<String>`. Other options are `<List<String>>`, `<CommaDelimitedList>`, or an AWS-specific type such as `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>`.
- **Default:** it becomes the SSM parameter name or path, for example `/app/prod/vpc-id`, not a literal value.
- **Secrets:** CloudFormation doesn't resolve `SecureString` through SSM parameter types. For those I'd switch to a dynamic reference, `{{resolve:ssm-secure:/path:version}}`, in the resource properties. Where the service supports it, I'd use Secrets Manager instead.
- **Constraints:** `AllowedValues`, `AllowedPattern` and `NoEcho` will need adjusting, because they apply to the SSM parameter name, not the value it resolves to.
