I haven't made any changes, and I can't make them in this session. I have no shell, so I can't run `gh`. I also have no file-write tool, so I can't create `SECURITY.md`. The skill's `scanning-and-response.md` reference was blocked on permissions, so I couldn't read its `SECURITY.md` guidance either.

**What I found:** the repo (`probe-sandbox`) has no `SECURITY.md` in the root, `.github/` or `docs/`. It has no `CONTRIBUTING.md`, `CLAUDE.md` or `AGENTS.md`. The README says nothing about security contacts.

**Two decisions I need from you:**
1. **Contact and response time:** which private channel should the policy name? Using GitHub's private vulnerability reporting alone would be simplest, and I'd rather not guess an email address. What acknowledgment time do you want to commit to, for example 3 business days?
2. **Repository slug:** what is the `OWNER/REPO` for this repo? I couldn't read the git remote.

**Draft `.github/SECURITY.md`:**
```markdown
# Security Policy

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub's
["Report a vulnerability"](../../security/advisories/new) form on the
Security tab. Do not open a public issue.

We acknowledge reports within 3 business days and aim to give a
remediation plan or status update within 14 days.

## Supported versions

Only the latest commit on `main` is supported.
```

**Enabling private vulnerability reporting.** This is an outward-facing change, so I'll apply it only after you approve. The call is `gh api -X PUT repos/OWNER/REPO/private-vulnerability-reporting`. I would then read it back with `gh api repos/OWNER/REPO/private-vulnerability-reporting --jq .enabled` and expect `true`.

To go ahead, either grant me shell and write access, or run the commands yourself. If you do, tell me the output and I'll check it. Confirm the contact and response time, and I'll finalize the text.
