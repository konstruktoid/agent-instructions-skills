# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | Bench A (`sources/bench-a.md`) | Bench B (`sources/bench-b.md`) |
|---|---|---|
| Author and date | Platform team, 2026-08-14 (lines 3) | Release team, 2026-09-09 (line 3) |
| Build under test | 3.0rc1, the first release candidate (line 5) | 3.0, the final release (line 5) |
| Hardware | x86-64, 16 cores, 64 GB (line 6) | ARM (aarch64), 16 cores, 64 GB (line 6) |
| Workload | Ten-minute production replay at 400 requests per second (line 7) | Same (line 7) |
| Repetitions | 5, median reported (line 8) | 5, median reported (line 8) |
| Baseline 2.9.4 p99 | 180 ms (line 12) | 176 ms (line 12) |
| Candidate p99 | 144 ms (line 13) | 175 ms (line 13) |
| p50 | 21 ms to 20 ms | 22 ms to 22 ms |
| Source's own reading | "p99 fell by 20 percent" (line 15) | "p99 did not change beyond run-to-run noise" (line 15) |

Neither source contains text written as an instruction to the reader.

## Findings

**Agreement.** Both sources use the same baseline (2.9.4), workload, core count, memory and repetition scheme. Both baselines are close (180 ms and 176 ms). Neither shows p99 getting worse.

**Conflict.** Bench A reports a drop from 180 ms to 144 ms, which is 20 percent (arithmetic checked). Bench B reports 176 ms to 175 ms, a 0.6 percent change, which it calls noise.

**Differences between the runs.** Two conditions differ, and the sources do not separate them:
1. Build: Bench A tested a release candidate. Bench B tested the final release. The sources do not say whether code changed between 3.0rc1 and 3.0.
2. Architecture: Bench A ran on x86-64. Bench B ran on ARM. Either difference could produce the gap on its own, or both could contribute.

**Source limitations.**
- Neither source reports variance, run-to-run spread or the noise threshold. Bench B's "noise" claim and Bench A's "20 percent" claim therefore cannot be checked against a stated spread.
- Neither source describes the parser rewrite beyond the title, so no mechanism explains an architecture-dependent or build-dependent effect.
- Each source tested only one architecture. Neither tested the other's configuration.

## Conclusions and conditions

1. **On x86-64, 3.0rc1 reduced p99 by about 20 percent in one benchmark.** Supported by Bench A. This holds for the release candidate, not for the final release, and rests on a single benchmark with no reported variance.
2. **On ARM, final 3.0 showed no p99 change beyond noise.** Supported by Bench B. This holds for aarch64 only, and no spread is given to define "noise".
3. **Final 3.0 reduces p99 in general.** Unresolved. The only test of the final release found no effect. The only test showing an effect used a different build on different hardware. The sources do not establish whether the cause is architecture or a code change between 3.0rc1 and 3.0. Recency alone (Bench B is later and tests the final build) does not settle this, because Bench B's different hardware could explain its result.
4. **Final 3.0 on x86-64.** No evidence in either source. A run of 3.0 on x86-64 would show whether the Bench A result carries over.

## Open questions

- Did the code change between 3.0rc1 and 3.0?
- Does 3.0 reduce p99 on x86-64? Does 3.0rc1 on ARM?
- What is the run-to-run spread in each benchmark?
- Which architecture does the production deployment use? The answer determines which result applies.

## Recommended next action

Run the final 3.0 and 2.9.4 on x86-64 with the Bench A workload, and run 3.0rc1 on ARM with the Bench B workload. Report the spread across repetitions. Together with the existing results, this separates the build effect from the architecture effect. Without it, do not state that 3.0 reduces p99 latency.

CONCLUSION: UNRESOLVED
