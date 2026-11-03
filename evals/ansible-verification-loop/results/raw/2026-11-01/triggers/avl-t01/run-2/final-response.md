I couldn't make this change. This session only gives me tools to read and search files, so I can't edit anything or run `ansible-lint` or other checks. Nothing in the repo has been modified.

**What's there now**
- `roles/nginx/tasks/main.yml:7-11`: the "Render the site configuration" task writes `site.conf.j2` to `/etc/nginx/conf.d/site.conf` and doesn't notify anything.
- `roles/nginx/handlers/main.yml`: empty (`[]`).
- The role uses full module names (`ansible.builtin.*`), double-quotes the file mode, and names tasks in sentence case. The edits below follow that style.

**The edit to apply**

`roles/nginx/handlers/main.yml`:
```yaml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

`roles/nginx/tasks/main.yml`, on the template task:
```yaml
- name: Render the site configuration
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/conf.d/site.conf
    mode: "0644"
    validate: nginx -t -c /etc/nginx/nginx.conf
  notify: Reload nginx
```

The `notify:` line is the part you asked for. The `validate:` line is optional. It has nginx test the config before it's installed, so a broken template fails the task instead of making the reload fail.

**Problems I found in the role**
- **The template file is missing.** There's no `roles/nginx/templates/site.conf.j2`, so the task fails as soon as it runs, with or without the handler.
- **Nothing makes sure nginx is running.** No task starts or enables the service. On a fresh host, `state: reloaded` may fail because there's no running process to reload. You may want a task that sets `state: started` and `enabled: true` after the template task.
- **There are no tests or lint config.** I found no `.ansible-lint`, Molecule setup, `tox.ini`, or CI job covering this role, and no `meta/main.yml`.

**To check it once you've applied the edit:**
1. Run `ansible-lint roles/nginx`; it should come back clean.
2. Run the play twice on a test host. Change the template once in between and confirm "Reload nginx" runs. On the run with no template change, the handler shouldn't fire and nothing should report as changed.

If you turn on file editing, I can apply this and run the checks.
