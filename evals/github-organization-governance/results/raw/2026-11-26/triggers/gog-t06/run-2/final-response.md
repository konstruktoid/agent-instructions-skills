I couldn't turn it on, for two reasons. I don't have a shell or GitHub API access in this session, so I can't change repository settings. I also don't know which repository you mean: I didn't find a remote URL configured in this workspace's git config.

To turn it on yourself, replace `OWNER/REPO` and run:

```bash
# Turn on secret scanning and push protection
gh api -X PATCH repos/OWNER/REPO \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'

# Check that the change took effect
gh api repos/OWNER/REPO --jq '.security_and_analysis'
```

In the check output, `secret_scanning.status` and `secret_scanning_push_protection.status` should both say `"enabled"`. Push protection blocks pushes that contain a detected secret; leave out the second `-f` line if you only want scanning.

- **Public repositories:** this works on any plan.
- **Private or internal repositories:** the organization needs GitHub Secret Protection (formerly part of GitHub Advanced Security). Without it, the call fails or the status stays `disabled`.
- **Organization overrides:** if the organization applies a security configuration to its repositories, it can override this per-repository setting. In that case, change it at the organization level.

You can also turn it on in the web interface under **Settings → Advanced Security** (named "Code security" on older layouts) **→ Secret Protection**.

If you tell me the `OWNER/REPO` and run the commands in a session where I have a shell, I can make the change and check the result for you.
