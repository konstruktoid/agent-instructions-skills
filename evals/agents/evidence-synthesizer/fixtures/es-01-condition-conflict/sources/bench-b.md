# Benchmark B: request latency, parser rewrite

Run by the release team on 2026-09-09.

- Build under test: 3.0, the final release
- Hardware: ARM (aarch64), 16 cores, 64 GB
- Workload: replay of ten minutes of production traffic at 400 requests per second
- Repetitions: 5, median reported

| Build | p50 (ms) | p99 (ms) |
|---|---|---|
| 2.9.4 | 22 | 176 |
| 3.0 | 22 | 175 |

p99 did not change beyond run-to-run noise.
