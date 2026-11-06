I haven't enabled secret scanning, and I can't from this session.

- **No way to call GitHub.** I have no shell and no `gh` CLI, so I can't call the GitHub API or change repository settings.
- **No repository found.** The workspace has no `origin` remote in its git config. My attempt to read the parent repo's config at `/repo/.git/config` was denied. I don't know which repository you mean, and I don't want to guess.

You can do it yourself in either of these ways:

1. **In the UI:** go to the repository's **Settings → Advanced Security** (called "Code security" in some versions). Enable **Secret Protection**, or **Secret scanning** on older plans. You can also turn on **Push protection** there.
2. **With the CLI:**
   ```bash
   gh api -X PATCH repos/OWNER/REPO \
     -f 'security_and_analysis[secret_scanning][status]=enabled'
   ```
   Add `-f 'security_and_analysis[secret_scanning_push_protection][status]=enabled'` if you want push protection too.

On a private repository, this needs GitHub Secret Protection (or Advanced Security) to be licensed. Public repositories have it for free.

If you give me the `OWNER/REPO` and a shell, I can run the command and read the setting back to confirm. Without a shell, I can only give you the command to run. I can also grant read access to the git config if you want me to find the remote.
