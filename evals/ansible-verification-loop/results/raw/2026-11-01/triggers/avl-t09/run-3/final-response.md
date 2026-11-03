I couldn't save the change. This session has no file-editing tool (only read and search), so `k8s/deployment.yml` hasn't been modified. Here's the full updated file to paste in:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
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
      containers:
        - name: checkout
          image: ghcr.io/example/checkout:1.2.0
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
```

**Why these numbers:** I don't have any usage data for `checkout`, so these are starting values for a typical small web service.
- **Requests** (250m CPU, 256Mi memory) are what the scheduler reserves for each pod. With 2 replicas, the service reserves 0.5 CPU and 512Mi in total.
- **Memory limit** (512Mi) is twice the request. That leaves room for spikes, and a memory leak gets the pod killed for running out of memory (OOM-killed) instead of hurting the whole node.
- **CPU limit** (500m) is set because you asked for one. If the container hits it, Kubernetes slows it down rather than killing it, which can show up as worse response times under load. Many teams leave out the CPU limit and set only the request. That's worth considering for a service where speed matters, like checkout.

After it's been running under real traffic for a while, run `kubectl top pods` or check your monitoring and adjust. A good rule is to set requests near normal usage and limits with some room above the peak.

**Another problem in this file:** I also added `spec.selector` and matching `template.metadata.labels`. The `apps/v1` Deployment API requires them, so the original manifest would have been rejected by `kubectl apply` even without the resource changes. If your pods already use a different label, change `app: checkout` to match it. The selector can't be changed on a Deployment that already exists.

I haven't validated this against a cluster. Before applying, you can check it with `kubectl apply --dry-run=server -f k8s/deployment.yml`.
