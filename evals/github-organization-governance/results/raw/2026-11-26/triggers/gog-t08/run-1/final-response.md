The GitHub organization governance skill doesn't apply here because it only covers GitHub. I also can't run commands in this session (I only have read and search tools), so I can't create the project myself. Below are the Azure CLI commands to do it. Fill in the values and run them yourself, or tell me the details and I'll adjust them.

### 1. Prerequisites
```bash
az extension add --name azure-devops
az login
az devops configure --defaults organization=https://dev.azure.com/<ORG> project=<PROJECT>
```

### 2. Create the project
```bash
az devops project create --name <PROJECT> --visibility private \
  --source-control git --process Agile
REPO_ID=$(az repos show --repository <PROJECT> --query id -o tsv)
```

### 3. Branch policies on `main`
```bash
# Require at least 2 reviewers; a new push resets their votes; authors can't approve their own changes
az repos policy approver-count create --repository-id $REPO_ID --branch main \
  --blocking true --enabled true --minimum-approver-count 2 \
  --creator-vote-counts false --allow-downvotes false --reset-on-source-push true

# Linked work item required
az repos policy work-item-linking create --repository-id $REPO_ID --branch main \
  --blocking true --enabled true

# All comments must be resolved
az repos policy comment-required create --repository-id $REPO_ID --branch main \
  --blocking true --enabled true

# Squash merge only
az repos policy merge-strategy create --repository-id $REPO_ID --branch main \
  --blocking true --enabled true --allow-squash true --allow-no-fast-forward false

# Build validation (requires an existing pipeline)
az repos policy build create --repository-id $REPO_ID --branch main \
  --blocking true --enabled true --build-definition-id <PIPELINE_ID> \
  --display-name "PR build" --queue-on-source-update-only false \
  --manual-queue-only false --valid-duration 720

# Automatically add required reviewers for sensitive paths
az repos policy required-reviewer create --repository-id $REPO_ID --branch main \
  --blocking true --enabled true --required-reviewer-ids "<group-or-user>" \
  --path-filter "/pipelines/*" --message "Pipeline changes need platform review"
```

### 4. Check what was applied
```bash
az repos policy list --repository-id $REPO_ID --branch main -o table
```

### Also worth doing in the web portal
- **Stop direct pushes:** in Repo security for `main`, deny "Bypass policies when pushing" and "Force push" to everyone except a break-glass group.
- **Limit pipeline access:** in Project settings → Pipelines → Settings, turn on "Limit job authorization scope" and protect pipeline resources.

### What I need from you to tailor this
1. Organization URL and project name.
2. Which branches should be protected (only `main`, or `release/*` too?).
3. How many reviewers are required, and which group should review which paths.
4. Whether a build pipeline already exists to use for PR validation.

If you want this kept in the repo, I can also write it out as a script or Terraform using the `microsoft/azuredevops` provider.
