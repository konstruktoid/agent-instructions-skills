# Load test: job queue migration

Run by the platform team. Same hardware, same job mix, 20 runs per queue, median reported.

| Queue | Median job latency (ms) |
|---|---|
| Current queue | 118 |
| Broker X | 121 |

The difference is inside the run-to-run spread of 6 ms.
