I can't change the file myself: this session only gives me read and search tools, with nothing for editing files or running commands. Below is the change to apply to `k8s/deployment.yml`:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: checkout
          image: ghcr.io/example/checkout:1.2.0
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

**Why these numbers:** The repo doesn't show what the checkout service actually uses, so these are conservative starting values for a small web service, not measured ones.
- **Requests** are what the scheduler reserves for each pod. 100m CPU and 128Mi memory are enough to place it without wasting space on the node.
- **Memory limit (256Mi):** if the container goes over this, Kubernetes kills it (OOMKilled). That's why it's set at twice the request, to leave room for spikes.
- **CPU limit (500m):** going over this slows the container down rather than killing it. Some teams leave the CPU limit off entirely to avoid that slowdown. If checkout is sensitive to response times, consider removing it and keeping only the request.

Once it's running, check real usage with `kubectl top pod -l app=checkout` or your metrics dashboards and adjust. The memory limit is the one to get right first.

**A separate problem:** this manifest will be rejected as it stands, with or without resources. `apps/v1` Deployments must have a `spec.selector` and matching `spec.template.metadata.labels`, and this one has neither. To fix it, add the following (the `app: checkout` label is my suggestion):

```yaml
spec:
  replicas: 2
  selector:
    matchLabels:
      app: checkout
  template:
    metadata:
      labels:
        app: checkout
    spec:
      ...
```

If you turn on file editing for this session, I can apply both changes and check the result with `kubectl apply --dry-run=client -f k8s/deployment.yml`.
