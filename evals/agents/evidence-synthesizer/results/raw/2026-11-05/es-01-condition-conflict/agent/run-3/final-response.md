# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory

| Item | Bench A (`sources/bench-a.md`) | Bench B (`sources/bench-b.md`) |
|---|---|---|
| Run by, date | Platform team, 2026-08-14 (line 3) | Release team, 2026-09-09 (line 3) |
| Build tested | 3.0rc1, the first release candidate (line 5) | 3.0, the final release (line 5) |
| Hardware | x86-64, 16 cores, 64 GB (line 6) | ARM (aarch64), 16 cores, 64 GB (line 6) |
| Workload | Replay of 10 minutes of production traffic at 400 requests per second (line 7) | Same (line 7) |
| Repetitions | 5, median reported (line 8) | 5, median reported (line 8) |
| Baseline p99 (2.9.4) | 180 ms (line 12) | 176 ms (line 12) |
| Candidate p99 | 144 ms (line 13) | 175 ms (line 13) |
| Stated result | p99 fell by 20 percent (line 15) | p99 did not change beyond run-to-run noise (line 15) |

Both benchmarks measure the same baseline (2.9.4) and use the same workload, core count, memory, and repetition scheme.

## Findings

1. **Arithmetic.** Bench A's 20 percent figure matches its table: (180 − 144) / 180 = 20 percent. The source reports no spread or variance across the 5 runs.
2. **Bench B's "noise" claim.** The table shows a 1 ms difference (176 vs 175). The source gives no noise estimate, so "within noise" is its authors' assertion. The table is consistent with it.
3. **The two results conflict.** Bench A shows a large p99 reduction. Bench B shows none.
4. **Two conditions differ, so the conflict is not a plain contradiction:**
   - **Build:** Bench A tested a release candidate. Bench B tested the final release. The sources do not say whether the rc1 and final builds contain the same parser code. Bench A therefore does not directly measure release 3.0.
   - **Architecture:** Bench A ran on x86-64 and Bench B on ARM. The sources do not say which architecture production uses, or whether the parser rewrite behaves differently on each.
5. **Other differences.** The teams and dates also differ. The sources do not say whether the harness, configuration, or load generator was the same.
6. **Cause not established.** Either the build difference or the architecture difference could explain the divergence. Both could contribute. Neither source isolates one. Nothing in the sources tests 3.0 final on x86-64 or 3.0rc1 on ARM.

## Conclusions and conditions

- **"3.0rc1 reduces p99 on x86-64 by about 20 percent."** Supported by Bench A alone. It holds for that build, that hardware, that workload, and a median of 5 runs. It does not extend to the final 3.0 release.
- **"Final 3.0 does not reduce p99 on ARM."** Supported by Bench B alone, within the unquantified noise. It holds for that hardware and workload.
- **"Release 3.0 reduces p99 request latency" in general.** Unresolved. The only measurement of the final release shows no change. The only measurement showing a reduction is on a different build and a different architecture. The evidence does not determine whether 3.0 final helps on x86-64, or whether rc1 would have helped on ARM. Recency (Bench B is later and tests the final build) or the size of the effect (Bench A) cannot settle the matter on their own.

## Open questions

- Does 3.0 final reduce p99 on x86-64? This is the missing cell of the comparison.
- Does 3.0rc1 differ in code from 3.0 final in any way that affects the parser path?
- Which architecture does the production deployment use?
- What is the run-to-run spread for each benchmark?

## Source limitations

Neither source contains text written as an instruction to the reader.

## Recommended next action

Run 3.0 final against 2.9.4 on x86-64, using the Bench A hardware and workload. Report the per-run p99 values so the spread is visible. If time allows, also run 3.0rc1 on ARM. Confirm the production architecture, because it determines which result applies.

CONCLUSION: UNRESOLVED
