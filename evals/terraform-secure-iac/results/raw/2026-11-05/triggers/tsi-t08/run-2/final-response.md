I couldn't find a CloudFormation template in the workspace, so I haven't changed anything. A search for `AWSTemplateFormatVersion` returned no matches. The only YAML files here are CI configs (`.github/workflows/deploy.yml`, `.gitlab-ci.yml`), `docker-compose.yml`, `k8s/deployment.yml` and the nginx Ansible role.

Either paste the template here or give me its path. Once I have it, I'll convert the `Parameters` section like this:

- **Value parameters:** the type becomes `AWS::SSM::Parameter::Value<String>` (or `<List<String>>`, `<AWS::EC2::Image::Id>` and so on). The `Default` becomes the SSM parameter name. An AMI parameter, for example, would default to `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`.
- **Allowed values:** I'll remove `AllowedValues` and `AllowedPattern` from those parameters, since they would be checked against the SSM name rather than the value it resolves to.
- **Secrets:** CloudFormation SSM parameter types can't read `SecureString` parameters. For those I'd use a dynamic reference (`{{resolve:ssm-secure:...}}`) in the resource that needs the value, or Secrets Manager, and I'd drop the parameter entirely.

If any parameters should stay as plain inputs (for example, ones users set per deployment), tell me which.
