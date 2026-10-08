I can't tell you which task reports changed, and I haven't changed anything. The workspace has no molecule scenario to run.

**What's in the workspace**
- There is no `molecule/` directory, `molecule.yml`, `converge.yml` or `verify.yml` anywhere.
- There is no `galaxy.yml`, so it isn't laid out as a collection.
- There is no `tox.ini`, `.ansible-lint`, `CLAUDE.md` or `CONTRIBUTING.md`.
- The only Ansible content is one role, `roles/nginx/`, with `defaults/main.yml`, `handlers/main.yml` and `tasks/main.yml`.

I checked the role's two tasks, and neither can be blamed for a changed result on a second run.
- `Install nginx` uses `package` with `state: present`, which is idempotent.
- `Render the site configuration` uses `template` with a fixed `mode`, which is idempotent as long as the rendered output is stable. The role has no `templates/site.conf.j2`, so that task would fail outright, not report changed.
- `handlers/main.yml` contains only `[]`, so nothing restarts or reloads nginx.

Guessing a fix from this would be speculation. I can't confirm a cause without the scenario and its output.

**What I need from you**
- The branch or path where the molecule scenario lives. It may be uncommitted, or on another branch. I'm on `eval-harness-delegation`, and git status shows only an untracked parent directory.
- Or the idempotence step's output, where the task marked `changed` appears in the second converge's recap. Please strip hostnames and home paths first.

Once I have either, I'll find the task and fix it. I'll then run `ansible-lint` and the full `molecule test`, with its idempotence check, to confirm the fix.
