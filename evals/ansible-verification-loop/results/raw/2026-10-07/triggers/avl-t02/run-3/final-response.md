I couldn't review `roles/postgres/tasks/main.yml` because it doesn't exist. The workspace has no `postgres` role, and no file or directory with "postgres" in its name. The only role's task file I found is `roles/nginx/tasks/main.yml`.

I haven't commented on package pinning or restart logic, because there's nothing to base it on. Checking `roles/nginx` instead would be a guess about what you meant.

Possible explanations:
- The role is on another branch. I'm on `eval-harness-delegation`.
- The file is somewhere else, for example a different repo or a path outside this workspace.
- You meant the `nginx` role.
- The file hasn't been committed or copied into this checkout yet.

Tell me which one it is, or give me the correct path, and I'll review it. I'll also read the role's `defaults`, `handlers`, and `meta` files, since restart logic usually lives in the handlers.
