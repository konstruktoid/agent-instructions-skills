I couldn't review it because `roles/postgres/tasks/main.yml` doesn't exist in this workspace. Searches for anything with "postgres" in its name, and for every `tasks/main.yml`, found nothing for postgres. The only role with a tasks file is `roles/nginx/tasks/main.yml`.

I haven't looked at the nginx role, since it isn't what you asked about, and I don't want to guess at pinning or restart logic in a file I haven't seen.

Which of these is it?
- **Wrong branch or directory:** the role may be on another branch or in another checkout. The current branch is `eval-harness-delegation`.
- **Different path:** the role may live under another name or path, such as a collection or `playbooks/`. Send me the path.
- **Nginx role:** you may have meant `roles/nginx/tasks/main.yml`. I can review that one instead.

Once I have the file, I'll read it with the role's `defaults/`, `handlers/` and `meta/`. I'll also run the repo's own lint and test setup, so the verdict on pinning and restarts isn't based on reading alone.
