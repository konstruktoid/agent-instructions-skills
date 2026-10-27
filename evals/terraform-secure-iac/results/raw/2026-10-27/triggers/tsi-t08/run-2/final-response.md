I couldn't find a CloudFormation template in this workspace. I searched for `AWSTemplateFormatVersion`, `AWS::` resource types and `Parameters:` blocks and got no matches. The YAML files here are a GitHub Actions workflow, a GitLab CI file, a Kubernetes deployment, a docker-compose file and an Ansible nginx role.

Could you give me the template's path, or paste its `Parameters` section here? Once I have it, I'll convert each parameter to the right SSM type:

| Current parameter | SSM parameter type |
|---|---|
| `String` (plain config value) | `AWS::SSM::Parameter::Value<String>` |
| `CommaDelimitedList` | `AWS::SSM::Parameter::Value<List<String>>` |
| AWS-specific types (e.g. `AWS::EC2::Image::Id`, `AWS::EC2::VPC::Id`) | `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>` etc. |

With an SSM type, the parameter's `Default` becomes the **name** of the SSM parameter, not the value. For example:

```yaml
Parameters:
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64
```

You can't do this for secrets. SSM parameter types don't support `SecureString`. Secrets need a dynamic reference instead, such as `{{resolve:ssm-secure:/path}}` or `{{resolve:secretsmanager:...}}`, written in the resource property and not in `Parameters`. I'll flag any parameters that need that.
