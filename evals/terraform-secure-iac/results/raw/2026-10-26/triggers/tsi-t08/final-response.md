I couldn't find a CloudFormation template in the working directory (`/repo/evals/terraform-secure-iac/results/raw/2026-10-26/triggers/tsi-t08/workspace`). I searched for YAML, JSON and `.template` files and for `AWSTemplateFormatVersion` or `Parameters:`. The only YAML files are `.github/workflows/deploy.yml`, `docker-compose.yml`, `k8s/deployment.yml`, `.gitlab-ci.yml` and the nginx role files, and none of them is a CloudFormation template.

Can you paste the template, or give me its path if it's somewhere else?

When I have it, I'll convert the parameters like this:
- **Value lookups:** parameters that fetch a value from Parameter Store, such as AMI IDs, get a type like `AWS::SSM::Parameter::Value<String>`. Their `Default` becomes the SSM parameter name, for example `/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`.
- **Other types:** I'll use `AWS::SSM::Parameter::Value<List<String>>`, `AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>` and similar where they fit.
- **Secrets:** I won't use SSM parameter types for secrets. CloudFormation doesn't support `SecureString` as a parameter type. For those I'd use a `{{resolve:ssm-secure:...}}` dynamic reference or Secrets Manager.
