I haven't set anything up yet. I have no way to reach your GitLab project from this session. Shell access is disabled, so I can't run `glab` or `curl` against the GitLab API, and no GitLab integration is connected. The repository security skill I have only covers GitHub, so it doesn't apply here either.

You can do it yourself in either of these ways:

**In the UI:** go to Settings → Repository → Protected branches → Add protected branch, then choose `main`. Set these values:
- Allowed to merge: Maintainers
- Allowed to push and merge: No one (or Maintainers, if you need direct pushes)
- Allowed to force push: off
- Code owner approval: on, if you use CODEOWNERS

**Via the API:**
```bash
curl --request POST --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects/<project-id>/protected_branches?name=main&push_access_level=0&merge_access_level=40&unprotect_access_level=40&allow_force_push=false"
```
If `main` is already protected, the API returns a conflict. In that case, delete the existing rule first, or update it with `PATCH`.

If you want me to do it, I need a session with shell access and a token with `api` scope. I would also need the GitLab host and project path or ID. I could also write the exact commands for your setup, and add a read-back check to confirm the rule applied.
