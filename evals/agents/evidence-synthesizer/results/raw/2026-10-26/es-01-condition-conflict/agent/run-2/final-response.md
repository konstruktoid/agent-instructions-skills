# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | `sources/bench-a.md` | `sources/bench-b.md` |
|---|---|---|
| Run by, date | Platform team, 2026-08-14 | Release team, 2026-09-09 |
| Build under test | 3.0rc1 (first release candidate) | 3.0 (final release) |
| Hardware | x86-64, 16 cores, 64 GB | ARM (aarch64), 16 cores, 64 GB |
| Workload | Replay of 10 minutes of production traffic at 400 requests per second | Same |
| Repetitions | 5, median reported | 5, median reported |
| Baseline p50 / p99 (2.9.4) | 21 ms / 180 ms | 22 ms / 176 ms |
| Candidate p50 / p99 | 20 ms / 144 ms | 22 ms / 175 ms |
| Stated result | "p99 fell by 20 percent" | "p99 did not change beyond run-to-run noise" |

Both files are source data. Neither contains instructions.

## Findings

**Source facts**
- Benchmark A shows p99 falling from 180 ms to 144 ms on x86-64 (bench-a.md, table). The 20 percent figure matches the arithmetic: 36 / 180 = 20%.
- Benchmark B shows p99 moving from 176 ms to 175 ms on ARM (bench-b.md, table). That is a 0.6% change, and the source attributes it to noise.
- The two benchmarks share the workload, the core count, memory, the repetition count and the aggregation method. They differ in three ways: the CPU architecture, the build, and the team and date.
- Neither source reports run-to-run variance, such as a range, standard deviation or confidence interval. Benchmark B's claim of "noise" and Benchmark A's claim of a 20 percent drop both come without a noise estimate.

**Agreement**
- The two sources agree that p50 did not change meaningfully (21 to 20 ms, and 22 to 22 ms).
- They agree on the baseline p99, within about 2% (180 and 176 ms).

**Conflict**
- The sources disagree on whether p99 improved: a 20% reduction versus no change.
- The two differ in build, architecture and team, so the sources cannot show which difference causes the divergence. These explanations are all candidates, and none is established:
  - The reduction is specific to x86-64, and the parser rewrite does not help on ARM.
  - The release candidate differed from the final 3.0 build, for example because a change between rc1 and final removed the gain.
  - Differences in team, setup or measurement procedure.
- Each explanation changes the answer. The first would make the claim true only on x86-64. The second would make Benchmark A irrelevant to release 3.0. The third would leave both results in doubt.

## Conclusions and conditions

1. **Release 3.0 reduces p99 latency in general: unsupported by the combined evidence.** Only Benchmark B tested the final 3.0 build, and it found no change. Benchmark A tested a different build, 3.0rc1.
2. **3.0rc1 reduced p99 on x86-64 by about 20%: supported by Benchmark A.** This holds only for that hardware, workload and build. No variance figure is given.
3. **Final 3.0 reduces p99 on x86-64: unresolved.** No source tests the final build on x86-64.
4. **Final 3.0 reduces p99 on ARM: unsupported.** Benchmark B contradicts it.
5. **The conflict cannot be resolved from these sources.** The newer date and the final-release label of Benchmark B do not make it more correct. It tested only ARM, so it cannot overturn an x86-64 result. Benchmark A's result is not transferable to the final build.

## Open questions

- Does final 3.0 reduce p99 on x86-64? This needs a run of 3.0 on the Benchmark A hardware.
- Does 3.0rc1 reduce p99 on ARM? Running it would separate the effect of architecture from the effect of the build.
- What is the run-to-run variance in each setup?
- What changed between 3.0rc1 and 3.0?
- Which hardware do the deployments in question use? The answer to the question depends on it.

## Recommended next action

Run the final 3.0 and 2.9.4 builds on the x86-64 hardware from Benchmark A, with the same replay workload and 5 repetitions. Record the spread of each run. If x86-64 shows the reduction, the claim holds on x86-64 only and the release notes should say so. If it shows no change, the rc1 gain did not reach the release. Until then, avoid stating that 3.0 reduces p99 latency.

CONCLUSION: UNRESOLVED
