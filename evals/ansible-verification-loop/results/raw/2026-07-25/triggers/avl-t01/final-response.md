I don't have file-editing or shell tools available in this session (only Glob, Grep, Read, and Skill), so I can't actually make the change or run `ansible-lint`/tests to verify it. Here's exactly what needs to change so you (or a session with Write/Edit/Bash tools) can apply it:

**`roles/nginx/handlers/main.yml`** — replace the empty `[]` with a reload handler:
```yaml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

**`roles/nginx/tasks/main.yml`** — add `notify` to the template task:
```yaml
- name: Render the site configuration
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/conf.d/site.conf
    mode: "0644"
  notify: Reload nginx
```

Note: this workspace has no `meta/main.yml`, `templates/`, molecule scenarios, `.ansible-lint`, or `tox.ini` for the role — it's a minimal probe-sandbox repo (per its README), so there's no existing test harness to extend or verification loop to run here. Want me to proceed once I have the right tools, or would you like to apply these two edits yourself?
