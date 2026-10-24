I didn't change anything, because there's no shell task in this repo that creates an account.

The only Ansible role is `roles/nginx`:
- `tasks/main.yml` has just two tasks: one installs nginx with `ansible.builtin.package` and one renders the site config with `ansible.builtin.template`.
- `handlers/main.yml` is empty (`[]`) and `defaults/main.yml` only sets `nginx_worker_processes`.

I also searched the whole workspace for `shell:`, `useradd` and `adduser`, and none of them appear anywhere.

So the task may be in another branch, another repo, or a file that hasn't been committed. If you paste it or tell me where it is, I'll swap it for the user module. The replacement usually looks like this:

```yaml
- name: Create the nginx service account
  ansible.builtin.user:
    name: "{{ nginx_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```

Unlike a shell command, the user module only makes a change when the account is missing or different, and it reports that correctly as changed or unchanged. That means you can drop any `creates:`, `changed_when:` or `failed_when:` workarounds. I'd also add `nginx_user` to `defaults/main.yml`. To get the details right, I need to see the original command's flags, such as the UID, group, home directory and login shell.
