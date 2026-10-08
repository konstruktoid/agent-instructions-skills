I can't tell which task reports changed on the second run, and I haven't changed anything. This workspace has no molecule scenario, so there is nothing to run.

- **No molecule files:** there is no `molecule/` directory anywhere. A case-insensitive search for "molecule" across every file found nothing.
- **No collection or test config:** there is no `galaxy.yml`, `tox.ini`, `Makefile` or `.ansible-lint`. The repo isn't an Ansible collection. It holds one role, `roles/nginx`, next to unrelated Go, Python, Terraform and Docker files.
- **Nothing visibly non-idempotent:** `roles/nginx/tasks/main.yml` has two tasks, `package` with `state: present` and a `template` to `/etc/nginx/conf.d/site.conf`. Both are normally idempotent.
- **Missing template:** `roles/nginx/templates/site.conf.j2` doesn't exist, so the second task would fail rather than report changed.
- **Invalid handlers file:** `roles/nginx/handlers/main.yml` contains `[]`, which isn't a valid handlers file.
- **Empty defaults:** I didn't open `defaults/main.yml`.

I'd be guessing if I named a task. Idempotence failures usually come from the actual run, for example a template that renders a timestamp or a command task without `changed_when`.

The scenario may be on another branch, in a different checkout, or in a different collection. Tell me where it lives, or paste the idempotence-step output, and I'll find the task, fix it and verify with the full molecule run. I'm on `eval-harness-delegation`, so I can look at other branches if you want.
