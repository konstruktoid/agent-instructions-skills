I changed nothing because the problem you described isn't in this repository. I searched the whole workspace for `.tf` and `.hcl` files and found only `infra/main.tf`. It has no `module` blocks, no Git `source`, no `terraform`/`required_providers` block, and no `.terraform.lock.hcl`. There's no unpinned Git ref and no provider constraint to fix.

The whole configuration is one resource (`infra/main.tf:1-10`): an `aws_security_group` called `bastion`. The repository's `README.md` says it's a "probe-sandbox" holding sample files for trigger evals, not a real infrastructure repo.

I also didn't run `fmt`, `validate` or `tflint`. I don't have a shell or file-edit tool in this session, so I couldn't have made the change either. And reading the supply-chain reference for this kind of fix was blocked by a permission prompt.

**Unrelated security issue:** `infra/main.tf:8` opens SSH (port 22) to `0.0.0.0/0`, so anyone on the internet can reach the bastion. Unless that's deliberate, limit `cidr_blocks` to known admin address ranges, or use SSM Session Manager and drop the ingress rule. It would also need a `description` on the group and on the rule.

**If you meant another repository or directory,** point me to it. The fix would be:
- **Module sources:** pin each Git source to a full commit SHA, e.g. `source = "git::https://example.com/org/mod.git?ref=<40-char-sha>"`. A tag is acceptable only if the remote protects it from being moved. Use HTTPS or SSH, with no credentials in the URL.
- **Provider constraints:** add a `terraform { required_version = "..." required_providers { aws = { source = "hashicorp/aws", version = "~> X.Y" } } }` block with the expected namespace. Then commit `.terraform.lock.hcl`, generated with `terraform providers lock` for every platform CI uses.
