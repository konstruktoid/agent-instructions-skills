I couldn't find a CloudFormation template in this workspace, so I haven't changed anything.

I searched for YAML, JSON and `.template` files, and for `AWSTemplateFormatVersion`, `AWS::` and `Parameters:`. None of the files here contain those markers. The workspace holds:

- a GitHub Actions workflow (`.github/workflows/deploy.yml`)
- `docker-compose.yml`
- a Kubernetes manifest (`k8s/deployment.yml`)
- `.gitlab-ci.yml`
- an Ansible `nginx` role

To go ahead, send me the template's path or paste its `Parameters` section here. Once I have it, I'll convert each parameter based on how it's used:

- **Plain values** (AMI IDs, subnet IDs, config strings) become `AWS::SSM::Parameter::Value<…>`. For example, `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>` with `Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`, or `AWS::SSM::Parameter::Value<String>` and `…<List<String>>` for your own parameter paths.
- **Secrets** (passwords, tokens) won't become SSM parameter types, because those types can't read `SecureString` values. I'll take those out of `Parameters` and replace each use with a `{{resolve:ssm-secure:/path}}` or `{{resolve:secretsmanager:…}}` dynamic reference. The secret then never shows up as a stack parameter.

I'll also mention any parameters that are better left as they are, such as values that change with each deployment.
