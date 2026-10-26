# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | Bench A (`sources/bench-a.md`) | Bench B (`sources/bench-b.md`) |
|---|---|---|
| Run by, date | Platform team, 2026-08-14 (lines 3) | Release team, 2026-09-09 (line 3) |
| Build under test | 3.0rc1, first release candidate (line 5) | 3.0, final release (line 5) |
| Hardware | x86-64, 16 cores, 64 GB (line 6) | ARM aarch64, 16 cores, 64 GB (line 6) |
| Workload | 10 min production replay, 400 req/s (line 7) | Same (line 7) |
| Repetitions | 5, median (line 8) | 5, median (line 8) |
| Baseline 2.9.4 p99 | 180 ms (line 12) | 176 ms (line 12) |
| Candidate p99 | 144 ms (line 13) | 175 ms (line 13) |
| p50 | 21 ms to 20 ms (lines 12-13) | 22 ms to 22 ms (lines 12-13) |
| Source's own claim | p99 fell 20 percent (line 15) | p99 unchanged within noise (line 15) |

## Findings

Source facts:
- Bench A reports a p99 drop from 180 ms to 144 ms. This is a 36 ms drop, or 20 percent, which matches the source's own arithmetic.
- Bench B reports 176 ms to 175 ms, a 1 ms difference. The source attributes it to noise.
- Neither source reports run-to-run variance, a spread, or a confidence interval. Bench B's "noise" claim and Bench A's reduction both rest on medians of 5 runs, with no stated variance.

Agreements:
- Same workload shape, core count, memory, repetition count, and baseline build (2.9.4).
- Baseline p99 is similar on both (180 vs 176 ms), so the baseline does not explain the divergence.

Conflict:
- The two sources give different p99 results for what the question calls "release 3.0". They differ in at least two conditions: the build (the rc1 in A, the final release in B) and the CPU architecture (x86-64 in A, aarch64 in B). They also differ in team and date.

Inference (mine, not stated in either source):
- Bench A tested a pre-release build, so it is not direct evidence about the final 3.0. Changes between rc1 and the release could have removed the gain. The sources do not say what changed.
- Bench B tested the final release but only on ARM. The gain seen in A could be specific to x86-64, or the rc1 could simply have differed from the release. The two benchmarks vary build and architecture together, so the sources cannot separate these causes.
- Both benchmarks describe the change as a "parser rewrite". Neither says whether the rewrite is the same code in rc1 and the final release.

## Conclusions and conditions

1. The final 3.0 release reduces p99 on x86-64: **unresolved**. The only x86-64 data is for rc1 (Bench A). The final release was not measured on x86-64.
2. The final 3.0 release reduces p99 on aarch64: **unsupported**. Bench B shows no change beyond noise (1 ms), though it gives no variance figures to quantify the noise.
3. 3.0rc1 reduces p99 on x86-64: **supported** by Bench A, for this workload at 400 req/s and with 5 median runs. It is not established beyond that, and Bench A has no variance data.
4. 3.0 reduces p99 in general, as the question asks: **unresolved**. The sources conflict, and the evidence does not establish which variable (build or architecture) explains the difference. I do not resolve it by taking the newer or the more favorable result.

Boundary: the sources cover one workload (400 req/s replay), one baseline (2.9.4), and two hardware types. They say nothing about other load levels, other architectures, or the production deployment platform.

## Open questions

- Which architecture does production run on? This determines which benchmark is relevant.
- What changed between 3.0rc1 and 3.0 in the parser code?
- What is the run-to-run spread of p99 in each benchmark?
- What is the result for the final 3.0 on x86-64, and for 3.0rc1 on aarch64?

## Next action

Run the final 3.0 against 2.9.4 on x86-64 hardware, ideally with the repetitions' individual values recorded. If one of the 3.0rc1 and 3.0 results on ARM is also taken, the build and architecture effects can be separated.

CONCLUSION: UNRESOLVED
