I didn't change anything, because there's no `shell` task in this repository to replace.

What I found:
- The only Ansible role is `roles/nginx`. Its tasks file, `roles/nginx/tasks/main.yml`, has two tasks: installing nginx with `ansible.builtin.package`, and rendering `site.conf.j2` with `ansible.builtin.template`.
- I searched every `.yml`/`.yaml` file for `shell`, `command` and `useradd` and got no matches. That covers the role's handlers and defaults, plus the CI, compose and k8s files.

The task may be on another branch, or in a role that isn't in this workspace. If you paste it or tell me where it lives, I'll convert it. Usually a `shell: useradd ...` task becomes something like:

```yaml
- name: Create the service account
  ansible.builtin.user:
    name: nginx_svc
    system: true
    shell: /usr/sbin/nologin
    home: /var/lib/nginx_svc
    create_home: false
    state: present
```

Unlike the shell version, this is idempotent: it won't fail or report "changed" when the account already exists. It also keeps the username out of a shell command line, so the name can't be used for injection. I'd match the exact options (`uid`, `group`, `groups`, `home`, `password`) to whatever your current `useradd` call passes.
