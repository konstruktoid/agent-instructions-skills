I couldn't edit `k8s/deployment.yml`. The Edit tool is disabled in this session, and I have no other tool that can write files. The file is unchanged.

This is the change I would make. Add it under the `checkout` container, at the same indent as `image`:

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

These numbers are a generic starting point for a small web service. Nothing in the repo tells me what `checkout` actually uses.

- **Requests:** these are what the scheduler reserves. 100m CPU and 128Mi memory should fit a light service.
- **CPU limit:** 500m gives headroom for bursts. Going over it only throttles the container.
- **Memory limit:** 256Mi is twice the request. Going over it gets the container OOM-killed, so if the service is JVM- or Node-based you will probably need more.

Before you rely on these, check real usage with `kubectl top pod` or your metrics, then adjust.

If you re-enable editing, or want to apply the snippet yourself, I can make the change and double-check the YAML.
