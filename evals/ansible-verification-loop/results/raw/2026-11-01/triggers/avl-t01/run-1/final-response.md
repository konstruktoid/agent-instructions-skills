I couldn't make this change. This session only gave me tools to read and search files, with no way to edit them or run commands. So nothing in the repo has changed, and nothing has been linted or tested. Here is exactly what to apply.

**`roles/nginx/handlers/main.yml`** (it currently holds an empty list, `[]`):
```yaml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

**`roles/nginx/tasks/main.yml`**, adding `notify` to the config task:
```yaml
- name: Render the site configuration
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/conf.d/site.conf
    mode: "0644"
  notify: Reload nginx
```

This follows the role's existing style: full module names like `ansible.builtin.*` and sentence-case task names. The `notify` value must match the handler name exactly.

**Problems I found in the repo:**
- **The template doesn't exist.** `roles/nginx/templates/site.conf.j2` is missing, so the config task will fail before the handler ever runs.
- **There's no linting or testing setup.** I found no `.ansible-lint`, `tox.ini`, Makefile or molecule scenarios, so there's nothing in the repo to verify the role against. Once the edits are in, the minimum check is to run `ansible-lint roles/nginx` and then run the role twice. On the first run the reload should happen; on the second it should report no changes and not reload.
- **A possible improvement (not applied):** nginx loads a broken config file when it reloads. Adding `validate: nginx -t -c %s` to the template task would catch bad configs before they reach the server. With a `conf.d` snippet it needs a wrapper config to test against, so I left it out.

**Security issues in `.github/workflows/deploy.yml`** (not related to this change):
- **Line 14** puts `${{ github.event.pull_request.title }}` straight into a shell command. Anyone who opens a PR can run commands in CI by choosing the title. Pass the title through an `env:` variable and quote it as `"$TITLE"` instead.
- **Line 7** sets `permissions: write-all`, which gives that job far more access than it needs. Reduce it to `contents: read`.

If you give me edit and shell access, I can apply all of this and run `ansible-lint`.
