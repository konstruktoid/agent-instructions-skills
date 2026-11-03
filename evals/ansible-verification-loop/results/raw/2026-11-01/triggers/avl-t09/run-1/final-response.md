I couldn't change `k8s/deployment.yml` because I only have read and search tools in this session. Here's the full updated manifest for you to paste in. It adds the CPU and memory settings, plus two fixes it was missing.

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
              cpu: "1"
              memory: 512Mi
```

**The values:** these are starting defaults for a typical small web service. Nothing in the repo shows how much `checkout` actually uses, so check them against real numbers (`kubectl top pods` or your metrics) before relying on them.
- **Requests** (`250m` CPU, `256Mi` memory) are what the scheduler reserves for each pod.
- **Memory limit** (`512Mi`) is a hard cap. If the container goes over it, Kubernetes kills it. If the app is a JVM or similar runtime, size its heap to fit inside this limit.
- **CPU limit** (`1`) slows the container down instead of killing it. If the service's response times matter a lot, some teams leave this limit off and keep only the request.

**Two other fixes:** an `apps/v1` Deployment needs `spec.selector`, and the pod template needs labels that match it. Without them the API server rejects the manifest, so I added `app: checkout` to both. If other resources, like a Service, already expect a different label, change it to match.

To check it before applying: `kubectl apply --dry-run=server -f k8s/deployment.yml`
