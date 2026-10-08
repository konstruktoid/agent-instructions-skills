I couldn't edit `k8s/deployment.yml`. The Edit tool is disabled in this session, and I have no other tool that writes files. Nothing has changed.

This is the change I would make. Add the `resources` block under the `checkout` container (line 12):

```yaml
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

- **Requests:** 100m CPU and 128Mi memory are a modest baseline for a small web service. The scheduler reserves this much for each of the 2 replicas.
- **Limits:** 500m CPU allows bursts, and CPU is throttled rather than killed when exceeded. 256Mi memory is 2× the request, and the pod is OOM-killed if it goes over.

These numbers are guesses, because the manifest has no data about the service's real usage. Check them against `kubectl top pod` or your metrics, and raise the memory limit if you see OOMKills. If you'd like me to apply the change, enable file editing and I'll add it.
