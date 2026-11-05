I haven't changed anything. This workspace has no GitLab access: I have no shell or GitLab API tools, and there's no `.git/config` remote I could find. The repository-security skill I have is for GitHub only, so I didn't use it for a GitLab project.

You can set it up yourself in either of these ways.

**In the UI:** go to **Settings → Repository → Protected branches** and select **Add protected branch**.
- Choose `main`.
- Set **Allowed to merge** to Maintainers, or to specific roles or groups.
- Set **Allowed to push and merge** to No one, so changes go through merge requests.
- Leave **Allow force push** off.
- On Premium or Ultimate, turn on **Require code owner approval** if you use CODEOWNERS.

**Through the API:**
```bash
curl --request POST --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects/<PROJECT_ID>/protected_branches?name=main&push_access_level=0&merge_access_level=40&allow_force_push=false"
```
Here `0` means no one and `40` means Maintainers. If `main` is already protected, this call returns a 409. In that case, delete the existing rule first or update it with `PATCH`.

To also require approvals and passing pipelines, set these under **Settings → Merge requests**:
- Pipelines must succeed.
- All threads must be resolved.
- A minimum number of approvals. This is an approval rule and may need Premium.

If you want me to run this, I need three things from you:
- The GitLab host and project path or ID.
- A way to reach it, such as a shell with `glab` or `curl` and a token with the `api` scope.
- The settings you want: who can merge, whether to require approvals, and whether to require code owners.
