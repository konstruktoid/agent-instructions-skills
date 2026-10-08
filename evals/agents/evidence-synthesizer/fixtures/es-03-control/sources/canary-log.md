# Canary rollout of release 4.2

Ten percent of production traffic went to 4.2 for 24 hours while the rest stayed on 4.1.

| Group | Cache hit ratio |
|---|---|
| Control, release 4.1 | 72 percent |
| Canary, release 4.2 | 94 percent |

Both groups received the same mix of requests.
