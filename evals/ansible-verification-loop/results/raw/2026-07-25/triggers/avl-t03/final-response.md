There's no molecule scenario in this workspace at all — I checked recursively and found no `molecule/` directory anywhere, and no reference to "molecule" in any file. This repo only contains a single `roles/nginx` role (tasks/handlers/defaults) plus unrelated infra/app code — it isn't set up as an Ansible collection, and there's nothing to run an idempotence check against.

Could you confirm the path or repo you meant? If you intended a different collection/workspace, point me at it and I'll pick up the idempotence issue from there.
