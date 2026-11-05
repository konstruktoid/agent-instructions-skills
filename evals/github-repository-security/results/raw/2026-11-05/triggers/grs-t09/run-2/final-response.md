I can't apply this from here. I have no shell or network tool in this session, so I can't call GitLab. The GitHub repository-security skill is also the wrong fit, because this is GitLab and not GitHub. Here is how to do it yourself.

**Note:** GitLab usually protects the default branch already. First check whether `main` is protected:

```bash
curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects/<PROJECT_ID>/protected_branches/main"
```

**If it isn't protected, or you want stricter settings:**

```bash
curl --request POST --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.example.com/api/v4/projects/<PROJECT_ID>/protected_branches" \
  --data "name=main" \
  --data "push_access_level=0" \
  --data "merge_access_level=30" \
  --data "unprotect_access_level=40" \
  --data "allow_force_push=false"
```

- `push_access_level=0` means no one can push directly, so changes go through merge requests.
- `merge_access_level=30` lets Developers and above merge.
- `unprotect_access_level=40` lets only Maintainers remove the protection.
- `allow_force_push=false` blocks force pushes.

**In the UI:** go to Settings → Repository → Protected branches, then choose `main` and set the allowed roles.

**Also worth setting:**
- Settings → Merge requests: require passing pipelines and resolved discussions.
- Approval rules, and CODEOWNERS approvals if you use them (some of these need a paid tier).

If you give me the GitLab host, the project ID or path, and the roles you want for push and merge, I'll tailor the commands. If you give me shell access with a token, I can run them and read the result back.
