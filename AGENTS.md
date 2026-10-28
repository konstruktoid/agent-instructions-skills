# AGENTS.md

This repository is what `instructions/` tells other projects to point their own `AGENTS.md` or
`CLAUDE.md` at. Working in it follows the same instructions documents it publishes:

- Python (`scripts/*.py`): follow `instructions/python_coding_instructions.md`.
- Bash (`agent-templates/hooks/*.sh`): follow `instructions/bash_coding_instructions.md`.
- Prose this repository writes about itself (`README.md`, `SECURITY.md`, `instructions/*.md`,
  `skills/**/*.md`, `agent-templates/*.md`, `docs/*.md`, and the eval READMEs and incident records
  under `evals/`): follow `instructions/written_language_instructions.md`.
- GitHub repository and organization configuration: follow
  `instructions/github_governance_instructions.md`.

Adding or changing a skill, an instructions document, or an agent template follows
[Adding new material](README.md#adding-new-material). Run the checks in
[Checks](README.md#checks) before calling a change done.
