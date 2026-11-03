# Evidence synthesis: does release 3.0 reduce p99 request latency?

## Evidence inventory
| Source | Build tested | Hardware | Workload | p99 2.9.4 → 3.x | Stated result |
|---|---|---|---|---|---|
| `sources/bench-a.md` (platform team, 2026-08-14) | **3.0rc1**, a release candidate | x86-64, 16 cores, 64 GB | 10 min production replay, 400 req/s, 5 reps, median | 180 → 144 ms | p99 fell 20% |
| `sources/bench-b.md` (release team, 2026-09-09) | **3.0**, the final release | aarch64, 16 cores, 64 GB | Same description, 5 reps, median | 176 → 175 ms | No change beyond run-to-run noise |

Both sources give p50 as well. A has 21 → 20 ms. B has 22 → 22 ms.

## Findings
**Source facts**
- A reports a 20% p99 reduction. (180 − 144) / 180 = 20%, so the arithmetic is correct (bench-a.md, lines 10–15).
- B reports a 1 ms p99 difference, which it calls noise (bench-b.md, lines 10–15).
- The two benchmarks differ in two respects.
  - Build: A tested 3.0rc1 and B tested final 3.0.
  - CPU architecture: A used x86-64 and B used aarch64.
- Workload, core count, memory, repetitions and aggregation are described identically.

**Inference**
- The sources conflict on the headline result, but they don't test the same thing. Neither tested final 3.0 on x86-64, and neither tested rc1 on ARM. So the conflict has at least two candidate explanations:
  1. The rc1 → final changes removed or changed the improvement.
  2. The improvement depends on architecture. It appears on x86-64 and not on aarch64.
  - A mix of both is also possible.
  - The sources don't distinguish these. Doing so would take a third run that varies only one factor.
- Neither file reports variance, the spread across repetitions, or the noise threshold. So B's "noise" claim and A's 20% claim can't be checked against each other.
- A's 2.9.4 baseline (180 ms) and B's (176 ms) are close. This weakly suggests the baselines are comparable across the two setups. It doesn't show that the hardware or harness are equivalent.

## Conclusions and their conditions
- **"3.0rc1 reduces p99 on x86-64 in this workload"**: supported by A alone. It holds only for that build, hardware and replay. It is not a claim about the final release.
- **"Final 3.0 reduces p99 on aarch64 in this workload"**: contradicted by B. The evidence shows no change.
- **"Release 3.0 reduces p99 latency" (general)**: unresolved. The only evidence on the final release (B) shows no reduction, and it's on a different architecture from the only positive evidence (A). The evidence for final 3.0 on x86-64 is absent. A is about a pre-release build, so it doesn't establish the claim for the release. B doesn't refute the claim for x86-64.
- I did not pick between the sources by recency, by team, or by which build is "final". Recency and finality favor B, but they don't establish that B's result would hold on x86-64.

## Open questions
1. What does final 3.0 do versus 2.9.4 on x86-64?
2. What does 3.0rc1 do on aarch64? That would isolate architecture from build changes.
3. What changed between rc1 and 3.0 in the parser rewrite?
4. What are the run-to-run spreads and the noise threshold in each benchmark?
5. Which architecture matters for the deployment the question is about? The question doesn't say.

## Recommended next action
Run final 3.0 against 2.9.4 on x86-64, using A's harness. If feasible, also run rc1 on aarch64. Report the spread across repetitions. If the question concerns one deployment platform, state it and use the matching result.

CONCLUSION: UNRESOLVED
