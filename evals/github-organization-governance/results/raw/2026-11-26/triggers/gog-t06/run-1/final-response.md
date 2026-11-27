I couldn't turn it on: I have no shell or GitHub API access in this session, and I can't tell which repository you mean (this workspace has no git remote configured). You can do it with one command. Replace `OWNER/REPO`:

```bash
gh api -X PATCH repos/OWNER/REPO \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'
```

The second line also turns on push protection, which blocks pushes that contain a detected secret. Remove that line if you only want scanning.

**Check that it worked:**

```bash
gh api repos/OWNER/REPO --jq '.security_and_analysis'
```

`secret_scanning.status` (and `secret_scanning_push_protection.status`, if you kept that line) should both say `"enabled"`.

**Things to know:**
- **Public repos:** secret scanning is free.
- **Private or internal repos:** you need GitHub Secret Protection (part of Advanced Security). Without it the request fails with a 422 error.
- **Permissions:** you need admin rights on the repo. If your organization enforces security settings through an organization-level policy, that policy may override this repo setting.
- **In the web interface:** Settings → Code security → Secret Protection → Enable.

If you tell me the repo's owner and name, I'll fill them into the commands.
