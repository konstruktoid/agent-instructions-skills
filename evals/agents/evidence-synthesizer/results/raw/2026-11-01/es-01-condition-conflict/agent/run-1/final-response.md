# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | Bench A (`sources/bench-a.md`, lines 1-15) | Bench B (`sources/bench-b.md`, lines 1-15) |
|---|---|---|
| Date | 2026-08-14 | 2026-09-09 |
| Run by | Platform team | Release team |
| Build under test | 3.0rc1, the first release candidate | 3.0, the final release |
| Hardware | x86-64, 16 cores, 64 GB | ARM (aarch64), 16 cores, 64 GB |
| Workload | Replay of 10 minutes of production traffic at 400 req/s | Same |
| Repetitions | 5, median reported | 5, median reported |
| 2.9.4 p50 / p99 | 21 ms / 180 ms | 22 ms / 176 ms |
| 3.0 p50 / p99 | 20 ms / 144 ms (rc1) | 22 ms / 175 ms (final) |
| Source's own reading | "p99 fell by 20 percent" | "p99 did not change beyond run-to-run noise" |

## Findings

Source facts:
- Bench A reports a p99 drop from 180 ms to 144 ms. This is a 36 ms reduction, or 20 percent, which matches the source's statement. The build is 3.0rc1, not the final release.
- Bench B reports a p99 of 176 ms for 2.9.4 and 175 ms for 3.0. The 1 ms difference is about 0.6 percent. The source attributes it to noise but gives no variance figure, so the noise claim cannot be checked.
- The two benchmarks share workload, core count, memory, repetition count, and aggregation method. They differ in three respects:
  - CPU architecture: x86-64 against aarch64.
  - Build: a release candidate against the final release.
  - Team and date: the platform team on 2026-08-14 against the release team on 2026-09-09.

Agreements:
- Both sources show the 2.9.4 baseline p99 in a narrow range (180 ms and 176 ms).
- Neither source shows 3.0 as worse at p99.

Conflict:
- The sources disagree on whether p99 improved. Bench A shows a 20 percent improvement. Bench B shows none.

Inference connecting the facts (not stated by either source):
- The architecture difference and the build difference are confounded. Neither source varies one while holding the other fixed. The sources do not say which factor caused the divergence, or whether it is a factor at all rather than measurement variation.
- Two explanations are consistent with the data:
  1. The parser rewrite improves p99 on x86-64 only, and the final 3.0 build still carries that gain on x86-64.
  2. The rc1 gain was removed or changed before the final release, and the final build has no p99 benefit on either architecture.
- The data do not distinguish these explanations. No source tests the final 3.0 on x86-64 or rc1 on ARM.

## Conclusions and conditions

1. **The final 3.0 release reduces p99 on ARM (aarch64): unsupported.** Bench B finds no change beyond noise. This holds only for the stated workload (400 req/s replay) and only if the source's noise judgment is accepted, as no variance data are given.
2. **The final 3.0 release reduces p99 on x86-64: unresolved.** The only x86-64 evidence is for rc1, not the final build. The evidence extends to the final build only if no relevant change occurred between rc1 and 3.0. No source states this.
3. **Release 3.0 reduces p99 in general: unresolved.** The sources conflict, and the differences between them (architecture and build) are confounded. Neither recency nor the "final release" label settles the question, because Bench B tests a different architecture. The question names no architecture, so a general claim is not established.

Limits of the evidence:
- Two runs, one workload shape, one load level (400 req/s).
- No variance, confidence intervals, or per-repetition data.
- No changelog or build diff between rc1 and 3.0.
- No x86-64 data for the final build.

## Open questions

- Does the final 3.0 build on x86-64 show the p99 gain seen with rc1?
- Does rc1 on ARM show a gain? This would isolate architecture from build.
- Did anything change between rc1 and 3.0 that affects the parser path?
- What is the run-to-run spread across the 5 repetitions on each platform?

## Recommended next action

Run the final 3.0 and 2.9.4 builds on x86-64 under the Bench A workload, and report the per-repetition p99 values. If the 20 percent gain reproduces, the architecture explanation gains support. If it does not, the rc1 gain did not carry into the final release. The question also needs a target platform. If the deployment is ARM only, Bench B already answers it with "no".

CONCLUSION: UNRESOLVED
