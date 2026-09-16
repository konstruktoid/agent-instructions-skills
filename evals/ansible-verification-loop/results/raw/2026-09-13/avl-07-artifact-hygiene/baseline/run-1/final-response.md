## What the tarball held

`molecule-logs/converge-2026-08-18.log` and `.env.yml` are tracked in git but were never listed in `galaxy.yml`'s `build_ignore`. `ansible-galaxy collection build` isn't git-aware — it copies the whole tree except `build_ignore` patterns — so both got swept into 1.4.0's tarball:

- **Internal hostname**: `buildnode-04.corp.example.net` (plus its IP `192.0.2.41` and the username `mbraun`), from a real molecule converge run log
- **Local credentials**: `.env.yml` — not read here per the secrets policy on `.env*` files, but its contents shipped verbatim

`.cache/`, `.github/`, and `collections/` (the vendored `community.general` copy, the likely bulk of the 31M) were already correctly excluded.

## Fix

Added two entries to `build_ignore` in `galaxy.yml:14-20`:
```yaml
build_ignore:
  - .ansible/
  - .cache/
  - .github/
  - collections/
  - molecule-logs/
  - .env.yml
```

## Verification — with a caveat

`ansible-core` isn't installed here, and installing it is a package install requiring your approval, so I didn't. I couldn't run the real `ansible-galaxy collection build` in this session. Instead I reimplemented the ignore-matching logic and ran it against the actual `git ls-files` output: `.env.yml` and `molecule-logs/converge-2026-08-18.log` now resolve as excluded, everything else unchanged. This confirms the fix's logic but isn't a substitute for the real tool.

To fully confirm, once `ansible-core` is available:
```
ansible-galaxy collection build --force && tar tzf platform-storage-1.4.0.tar.gz | grep -E 'molecule-logs|\.env\.yml'
```
should return nothing.

The files stay on disk as requested — only `galaxy.yml` changed. `/clear` before starting anything unrelated.
