I couldn't make this change. My tools here only let me read and search files, not edit them or run commands, so nothing in the repo has been modified. Here's the change, ready to apply.

**`roles/nginx/handlers/main.yml`** (currently just `[]`):

```yaml
---
- name: Reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```

**`roles/nginx/tasks/main.yml`**: add `notify` to the template task:

```yaml
- name: Render the site configuration
  ansible.builtin.template:
    src: site.conf.j2
    dest: /etc/nginx/conf.d/site.conf
    mode: "0644"
  notify: Reload nginx
```

This uses the same full `ansible.builtin.*` module names and `"0644"` quoting the role already uses. A handler only fires when its task reports a change, so nginx reloads only when the rendered config actually differs. `reloaded` applies the new config without dropping connections, where `restarted` would drop them.

**Problems in the role:**
- **The template file is missing.** The task uses `src: site.conf.j2`, but there's no `roles/nginx/templates/` directory, so this task fails whether or not you add the handler.
- **A broken config will still be reloaded.** If you want nginx to check the config before using it, add `validate: nginx -t -c %s` to the template task. That only works if the file is a complete nginx config. For a `conf.d` snippet like this one, `nginx -t` on its own would fail, so you'd need a different check.

**Not verified:** I couldn't run `ansible-lint` or any tests. The repo also has no lint config, Molecule setup or `tox.ini` for this role, so there's no test suite to run. Once the change is in, I'd run:

```sh
ansible-lint roles/nginx
```

and then run a playbook that uses the role twice. The second run should report no changes and no handler run.
