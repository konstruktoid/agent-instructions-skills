# Evidence report: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | Bench A (`sources/bench-a.md`) | Bench B (`sources/bench-b.md`) |
|---|---|---|
| Run by, date | Platform team, 2026-08-14 (lines 3) | Release team, 2026-09-09 (line 3) |
| Build under test | 3.0rc1, the first release candidate (line 5) | 3.0, the final release (line 5) |
| Hardware | x86-64, 16 cores, 64 GB (line 6) | ARM (aarch64), 16 cores, 64 GB (line 6) |
| Workload | Ten-minute replay of production traffic, 400 req/s (line 7) | Same (line 7) |
| Repetitions | 5, median reported (line 8) | 5, median reported (line 8) |
| Baseline p50 / p99 (2.9.4) | 21 ms / 180 ms (line 12) | 22 ms / 176 ms (line 12) |
| Candidate p50 / p99 | 20 ms / 144 ms (line 13) | 22 ms / 175 ms (line 13) |
| Source's own reading | "p99 fell by 20 percent" (line 15) | "p99 did not change beyond run-to-run noise" (line 15) |

## Findings

**Agreement.** Both benchmarks use the same workload design, the same core and memory counts, the same repetition count, and the same baseline build (2.9.4). Baseline p99 is similar in both: 180 ms and 176 ms.

**Apparent conflict.** Bench A reports a 36 ms p99 drop (180 to 144 ms; 36/180 is 20 percent, which matches its stated figure). Bench B reports a 1 ms drop (176 to 175 ms) and calls it noise.

**The two sources differ in conditions, so they do not test the same thing.**
- Build: Bench A tests a release candidate. Bench B tests the final release. Neither source says whether the code differs between 3.0rc1 and 3.0.
- Architecture: Bench A ran on x86-64. Bench B ran on ARM (aarch64). Neither source reports both architectures for the same build.
- Team and date: the runs are about four weeks apart and by different teams. The sources do not describe how the environments were set up.

These differences are confounded. Build and architecture changed together between the benchmarks, so the sources cannot show which one accounts for the different results.

**Source limitations.**
- Each source reports medians of 5 runs and gives no spread, variance or confidence interval. Bench B's "within noise" and Bench A's "fell by 20 percent" are the authors' readings, and the sources give no data to check them. Bench A does not say whether 36 ms exceeds its run-to-run noise.
- p99 over a ten-minute replay at 400 req/s rests on about 240,000 requests per run, so roughly 2,400 requests sit in the tail. The sources do not discuss tail stability.
- Neither source says whether the replayed traffic was identical across builds or whether the hardware was otherwise idle.

## Conclusions and conditions

1. **The final 3.0 release reduces p99 on ARM: unsupported.** Bench B measured the final release on ARM and found no change beyond noise (175 ms against 176 ms). It holds for that hardware and that workload only.
2. **3.0rc1 reduced p99 on x86-64 by about 20 percent: supported by Bench A alone.** It holds only for the release candidate on that hardware. The sources do not extend it to the final build.
3. **The final 3.0 release reduces p99 on x86-64: unresolved.** No source tests the final build on x86-64. Reaching that conclusion from Bench A requires an assumption that rc1 and the final build are equivalent. The sources do not establish that assumption.
4. **The general claim that 3.0 reduces p99: unresolved.** The sources point in opposite directions and differ in two conditions at once. Preferring the newer or the final-release source, or the larger effect, would settle the conflict by preference alone, which the evidence does not justify.

## Open questions

- Does 3.0 reduce p99 on x86-64? Run the final build there.
- Does 3.0rc1 reduce p99 on ARM? Run the release candidate there. Together with the previous run, this separates the effect of the build from the effect of the architecture.
- What is the run-to-run spread of p99 in each benchmark?
- Which code changed between 3.0rc1 and 3.0?
- Which architecture does the intended deployment use? The question does not name one, so the answer may depend on it.

## Recommended next action

Run the final 3.0 build and 2.9.4 on x86-64 using Bench A's setup. Report per-run p99 values and not only medians. If the reduction appears there but not on ARM, the result is architecture-specific and the answer to the question depends on the deployment target. If no reduction appears, the rc1 result most likely came from a code difference or from noise.

CONCLUSION: UNRESOLVED
