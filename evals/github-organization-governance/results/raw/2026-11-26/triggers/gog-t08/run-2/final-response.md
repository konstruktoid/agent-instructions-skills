I can't set this up from here. This session has no shell or Azure DevOps access, so I can't run `az` commands. Your workspace also has no Azure DevOps setup to start from: it has GitHub Actions, GitLab CI and Jenkins pipelines, but no `azure-pipelines.yml`. (The GitHub organization governance skill I have doesn't apply, since it only covers GitHub.)

Here's a script you can run with the Azure CLI. Fill in the placeholders first.

```bash
# One-time setup
az extension add --name azure-devops
az login
ORG=https://dev.azure.com/<your-org>
PROJECT=<project-name>
REPO=<repo-name>
BRANCH=main
az devops configure --defaults organization=$ORG

# 1. Create the project (Git, private, Agile process)
az devops project create --name "$PROJECT" --source-control git \
  --visibility private --process Agile
az devops configure --defaults organization=$ORG project="$PROJECT"

# 2. Create the repo (the project also comes with a default repo named after it)
az repos create --name "$REPO"
REPO_ID=$(az repos show --repository "$REPO" --query id -o tsv)
# Branch policies need the branch to exist: push an initial commit to $BRANCH first.

# 3. Branch policies on main
# Require at least 2 reviewers; reset votes on new pushes; author can't approve own PR
az repos policy approver-count create --repository-id $REPO_ID --branch $BRANCH \
  --blocking true --enabled true --minimum-approver-count 2 \
  --creator-vote-counts false --allow-downvotes false --reset-on-source-push true

# Linked work item required
az repos policy work-item-linking create --repository-id $REPO_ID --branch $BRANCH \
  --blocking true --enabled true

# All PR comments must be resolved
az repos policy comment-required create --repository-id $REPO_ID --branch $BRANCH \
  --blocking true --enabled true

# Only squash merges allowed
az repos policy merge-strategy create --repository-id $REPO_ID --branch $BRANCH \
  --blocking true --enabled true --allow-squash true \
  --allow-no-fast-forward false --allow-rebase false --allow-rebase-merge false

# Build validation (needs an existing pipeline; get its ID from `az pipelines list`)
az repos policy build create --repository-id $REPO_ID --branch $BRANCH \
  --blocking true --enabled true --build-definition-id <PIPELINE_ID> \
  --display-name "CI" --queue-on-source-update-only false --manual-queue-only false \
  --valid-duration 720

# Optional: auto-add a required reviewer group for sensitive paths
az repos policy required-reviewer create --repository-id $REPO_ID --branch $BRANCH \
  --blocking true --enabled true --required-reviewer-ids "<group-or-user-email>" \
  --path-filter "/infra/*;/k8s/*" --message "Platform team review required"

# 4. Check what was applied
az repos policy list --repository-id $REPO_ID --branch $BRANCH -o table
```

**Notes:**
- **Who can bypass:** branch policies don't stop project admins from bypassing them. Under Project Settings → Repositories → Security, remove "Bypass policies when completing pull requests" and "Bypass policies when pushing" from everyone who shouldn't have them.
- **Applying to many repos:** to apply the policies to every repo in the project, leave out `--repository-id`. That creates project-wide policies for the branch.
- **Requirements:** the build validation policy only works once a pipeline exists. Your repo has GitHub Actions, GitLab CI and Jenkins configs, so you'd need to add an `azure-pipelines.yml` first.

If you give me the organization and project names, reviewer count, merge strategy and branches to protect, I can tailor the script. I can also write an `azure-pipelines.yml` for the build validation step, ported from your existing CI config.
