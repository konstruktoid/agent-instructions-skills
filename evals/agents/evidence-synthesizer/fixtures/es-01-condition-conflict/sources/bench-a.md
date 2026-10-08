# Benchmark A: request latency, parser rewrite

Run by the platform team on 2026-08-14.

- Build under test: 3.0rc1, the first release candidate
- Hardware: x86-64, 16 cores, 64 GB
- Workload: replay of ten minutes of production traffic at 400 requests per second
- Repetitions: 5, median reported

| Build | p50 (ms) | p99 (ms) |
|---|---|---|
| 2.9.4 | 21 | 180 |
| 3.0rc1 | 20 | 144 |

p99 fell by 20 percent.
