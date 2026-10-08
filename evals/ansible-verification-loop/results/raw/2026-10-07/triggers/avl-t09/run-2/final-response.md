I couldn't add the resource limits. The Edit tool is disabled in this session, so `k8s/deployment.yml` is unchanged. I also have no other tool here that writes to files.

This is the block I would add under the `checkout` container, after `image:` at line 12:

```yaml
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

These numbers are generic starting values for a small web service. I haven't seen the service's real usage. The requests are what the scheduler reserves, and the limits are the ceiling. Memory over the limit gets the container OOM-killed. CPU over the limit gets throttled. Check them against `kubectl top pod` or your metrics, and raise the memory limit if the service is a JVM or Node app that needs more headroom.

You can paste the block in yourself, or enable an edit tool and I'll apply it.
