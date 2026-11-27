I couldn't turn it on. I can't run commands or call the GitHub API in this session, and the workspace doesn't contain a git repository with a remote, so I also can't tell which repository you mean.

Here are two ways to do it yourself (replace `OWNER/REPO`):

**With the GitHub CLI**

```bash
# Turn on secret scanning and push protection
gh api -X PATCH repos/OWNER/REPO --input - <<'EOF'
{
  "security_and_analysis": {
    "secret_scanning": { "status": "enabled" },
    "secret_scanning_push_protection": { "status": "enabled" }
  }
}
EOF

# Check that it worked
gh api repos/OWNER/REPO --jq '.security_and_analysis'
```

**In the web UI:** go to the repository's **Settings → Advanced Security** (called "Code security" on some plans) and turn on **Secret Protection**. Push protection can be turned on in the same place.

Some things to know:
- **Public repositories:** secret scanning is free. Push protection (which blocks pushes that contain secrets) is optional, so remove that line if you don't want it.
- **Private or internal repositories:** these need GitHub Secret Protection (part of Advanced Security), which is a paid license. Without it, the API call returns an error or the setting stays `disabled`. That's why the check step matters.
- **Organization settings:** if the repository belongs to an organization that applies a security configuration, that configuration can override this per-repo setting. If the change doesn't stick, look under **Org settings → Advanced Security → Configurations**.
- **Permissions:** you need admin rights on the repository.

If you tell me the `OWNER/REPO` and run the commands in a session where I have shell access, I can do it and check the result.
