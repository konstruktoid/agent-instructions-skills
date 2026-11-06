# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | `sources/bench-a.md` | `sources/bench-b.md` |
|---|---|---|
| Date and runner | 2026-08-14, platform team (lines 3) | 2026-09-09, release team (line 3) |
| Build under test | 3.0rc1, the first release candidate (line 5) | 3.0, the final release (line 5) |
| Hardware | x86-64, 16 cores, 64 GB (line 6) | ARM (aarch64), 16 cores, 64 GB (line 6) |
| Workload | Replay of ten minutes of production traffic at 400 requests per second (line 7) | Same (line 7) |
| Repetitions | 5, median reported (line 8) | Same (line 8) |
| Baseline 2.9.4 p50 / p99 | 21 ms / 180 ms (line 12) | 22 ms / 176 ms (line 12) |
| Candidate p50 / p99 | 20 ms / 144 ms (line 13) | 22 ms / 175 ms (line 13) |
| Stated result | "p99 fell by 20 percent" (line 15) | "p99 did not change beyond run-to-run noise" (line 15) |

Neither source contains text addressed to the reader as an instruction.

## Findings

**Agreement.**
- Both benchmarks use the same workload, repetition count and aggregation.
- Both compare against 2.9.4.
- Both report a p50 that is nearly unchanged.
- Both baselines are close (180 ms and 176 ms).

**Conflict.**
- bench-a reports a p99 drop from 180 ms to 144 ms. The 20 percent figure matches that arithmetic (36 / 180).
- bench-b reports 176 ms to 175 ms, which it describes as no change.

**Differences that could account for the conflict.** These are candidate explanations. The sources do not test them.
- **Build.** bench-a tested a release candidate, not the final release. The sources do not say whether 3.0rc1 and 3.0 contain the same parser code.
- **Architecture.** bench-a ran on x86-64 and bench-b on aarch64. The sources do not show whether the parser rewrite behaves differently on the two.
- **Team and environment.** The teams differ. Neither source describes system configuration, so these are not comparable.

**Source limitations.**
- Neither source reports run-to-run variance, a confidence interval or the five individual results.
- bench-b's "noise" claim is therefore an assertion with no quantified noise band.
- bench-a's 20 percent drop is also unsupported by any variance figure.
- Neither source varies architecture and build independently. The data cannot separate the two as the cause.
- The 3.0 release, which is the subject of the question, was measured only on aarch64, and only in bench-b.
- The x86-64 result applies only to a release candidate.

## Conclusions and conditions

1. **"The final 3.0 release reduces p99 on aarch64": unsupported.** bench-b shows 176 ms to 175 ms, and the source itself attributes the difference to noise. This holds under bench-b's workload and hardware.
2. **"3.0rc1 reduces p99 on x86-64": supported, with limits.** bench-a shows 180 ms to 144 ms. This holds only for that build, hardware and workload, and without variance data.
3. **"Release 3.0 reduces p99 in general": unresolved.** The only evidence for a reduction covers a different build and different hardware from the only evidence on the final release. The two sources conflict on the question as asked. Neither preference for the later date, nor the final-release label, nor the larger effect size settles it. No source measures the final 3.0 on x86-64, or 3.0rc1 on aarch64. The question names no hardware, so a conclusion for either platform alone does not answer it.

## Open questions

- Does 3.0 differ from 3.0rc1 in code that affects the parser or request path?
- Does the parser rewrite perform differently on x86-64 and aarch64?
- What is the run-to-run spread of p99 across the five repetitions on each platform?
- Which hardware does the question's deployment target use?

## Recommended next action

Run the final 3.0 and 2.9.4 on x86-64 with the bench-a workload, and report all five repetitions. If the reduction appears, the architecture is the likely cause of the gap. If it does not, the difference between 3.0rc1 and 3.0 is the likely cause. Otherwise, state the claim only for the platform and build that were measured.

CONCLUSION: UNRESOLVED
