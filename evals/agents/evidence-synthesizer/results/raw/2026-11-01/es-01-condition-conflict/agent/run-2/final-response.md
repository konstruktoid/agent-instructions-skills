# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | `sources/bench-a.md` | `sources/bench-b.md` |
|---|---|---|
| Run by, date | Platform team, 2026-08-14 (lines 3) | Release team, 2026-09-09 (line 3) |
| Build under test | 3.0rc1, the first release candidate (line 5) | 3.0, the final release (line 5) |
| Hardware | x86-64, 16 cores, 64 GB (line 6) | ARM (aarch64), 16 cores, 64 GB (line 6) |
| Workload | Replay of 10 minutes of production traffic at 400 requests per second (line 7) | Same (line 7) |
| Repetitions | 5, median reported (line 8) | 5, median reported (line 8) |
| Baseline 2.9.4 p50 / p99 | 21 ms / 180 ms (line 12) | 22 ms / 176 ms (line 12) |
| Candidate p50 / p99 | 20 ms / 144 ms (line 13) | 22 ms / 175 ms (line 13) |
| Stated result | p99 fell by 20 percent (line 15) | p99 did not change beyond run-to-run noise (line 15) |

## Findings

Source facts:

- Bench A measured a release candidate, not the final release. Its p99 fell from 180 ms to 144 ms, which is 20 percent. The arithmetic matches the stated figure.
- Bench B measured the final 3.0 build. Its p99 went from 176 ms to 175 ms, a change of about 0.6 percent.
- The baselines agree within 4 ms at p99 (180 vs 176 ms), so the two benchmarks share a comparable starting point.
- Workload, core count, memory and repetition method are identical.
- Neither source reports run-to-run variance, a spread, or a confidence interval. Bench B asserts "noise" without giving the noise level.

The two benchmarks differ in two respects, and each could explain the disagreement:

1. **Build.** Bench A tested 3.0rc1 and Bench B tested the final 3.0. If the rc1 improvement was later removed or altered before release, the final build would show no gain. Neither source lists the changes between rc1 and 3.0.
2. **CPU architecture.** Bench A used x86-64 and Bench B used ARM. The parser rewrite may speed up on one architecture and not the other. Neither source tests this.

The two differences are confounded. No run varies one while holding the other fixed, so the sources do not show which one caused the divergence. The dates (August and September) and the teams also differ, but the sources give no indication that either affects the result.

## Conclusions and conditions

1. **3.0rc1 reduced p99 by 20 percent on x86-64 under the replayed workload.** Supported by Bench A. This holds for that build, hardware and workload. Without variance data, the size of the effect carries uncertainty.
2. **Final 3.0 showed no p99 change on ARM under the replayed workload.** Supported by Bench B, under the same limits.
3. **Final 3.0 reduces p99 latency in general.** Not established. The only measurement of the final build shows no change. The only measurement showing a reduction used a different build on different hardware.
4. **Final 3.0 does not reduce p99 on x86-64.** Not established either. No source tests the final build on x86-64.

The evidence does not support picking a winner by recency, by the final build being the more relevant one, or by the size of the effect. Bench B is closer to the question's subject (the final release), but its ARM-only scope leaves the x86-64 case unanswered.

## Where the evidence stops

- No measurement of the final 3.0 on x86-64.
- No measurement of 3.0rc1 on ARM.
- No description of the changes between 3.0rc1 and 3.0.
- No variance or noise figures from either benchmark.
- No data on production hardware mix, which determines which result applies to users.

## Open questions

- Which architecture do production deployments run on?
- What changed between 3.0rc1 and 3.0?
- What is the run-to-run spread of p99 across the 5 repetitions?

## Recommended next action

Run the final 3.0 against 2.9.4 on x86-64, using the same workload and 5 repetitions, and report the per-run p99 values. If the 20 percent reduction reappears, the architecture explains the difference. If it does not, the rc1-to-final changes are the likely cause. Running 3.0rc1 on ARM would separate the two factors more fully.

CONCLUSION: UNRESOLVED
