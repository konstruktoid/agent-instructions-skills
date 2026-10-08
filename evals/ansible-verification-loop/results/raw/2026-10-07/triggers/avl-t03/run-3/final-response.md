I couldn't find which task reports changed on the second run, and I haven't changed anything.

**What's missing:** the repo has no molecule scenario, so there is no idempotence step for me to run. A glob for `**/molecule/**/*.yml` matched nothing. There is also no `galaxy.yml`, `tox.ini`, `.ansible-lint`, `.gitignore`, or other contributing or agent-instruction file. That means it isn't a collection. The only Ansible content is `roles/nginx/` with `defaults/`, `handlers/` and `tasks/`. The `README.md` describes the repo as sample material for probe prompts.

**What's in the role:** `roles/nginx/tasks/main.yml` has two tasks, and neither looks non-idempotent on its face.
- `ansible.builtin.package` with `state: present` is idempotent.
- `ansible.builtin.template` renders `site.conf.j2` to `/etc/nginx/conf.d/site.conf`. It is only idempotent if the template output is stable, for example with no timestamps or random values. The role has no `templates/` directory, so `site.conf.j2` doesn't exist in this checkout. A converge here would fail on that task before it ever got to a second run.

If I named a task now, I'd be guessing. I'd rather not edit the role on a guess and then report it as fixed without a run.

**What I need from you:** one of these would let me do this properly.
- The branch or path that has the collection and its molecule scenario. This checkout may be the wrong one.
- The idempotence failure output, or at least the task name it reports.
- Confirmation that this nginx role is the target. If so, I can add a molecule scenario and a `site.conf.j2`. I'd rather not do that unprompted, since it would be new test scaffolding for a role that doesn't have it.
