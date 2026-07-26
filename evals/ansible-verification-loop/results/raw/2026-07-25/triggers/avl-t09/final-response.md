I don't have write access enabled in this session (only Glob/Grep/Read/Skill tools are available), so I can't apply the edit directly. Here's the change needed in `k8s/deployment.yml`:

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

These are conservative starting values for a small service (100m/128Mi requested, capped at 500m/256Mi) — adjust based on actual observed usage if you have metrics. Please enable the Edit tool (or apply this diff yourself) and I can proceed, or you can paste it in directly.
