I didn't change anything, because I couldn't find a `shell` task that creates an account anywhere in this repository.

The only Ansible role is `roles/nginx`:

- `roles/nginx/tasks/main.yml` has two tasks: installing nginx with `ansible.builtin.package`, and rendering `site.conf` with `ansible.builtin.template`.
- `roles/nginx/handlers/main.yml` is empty (`[]`).
- `roles/nginx/defaults/main.yml` only sets `nginx_worker_processes`.

I also searched the whole repo for `shell`, `command`, `useradd` and `adduser` and found nothing related to creating accounts.

The task may be on another branch, in another repo, or not committed yet. Can you point me to the file or paste the task? Once I can see it, I'll swap it for an `ansible.builtin.user` task that keeps the same settings (name, uid, group, shell, home, system account). Running it twice won't change anything. For example:

```yaml
- name: Create the nginx service account
  ansible.builtin.user:
    name: "{{ nginx_user }}"
    system: true
    shell: /usr/sbin/nologin
    create_home: false
    state: present
```
