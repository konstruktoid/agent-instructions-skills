# Evidence report: does Broker X reduce median job latency?

## Evidence inventory

| ID | Source | Location | Claim or measurement |
|---|---|---|---|
| L1 | `sources/load-test.md` | lines 3-8 | The platform team ran the test on the same hardware with the same job mix, 20 runs per queue, and reported the median. Median job latency was 118 ms for the current queue and 121 ms for Broker X. |
| L2 | `sources/load-test.md` | line 10 | The difference is inside the run-to-run spread of 6 ms. |
| V1 | `sources/vendor-note.md` | lines 3-4 | Customers report that Broker X makes jobs "up to 40 percent faster". The note says no test setup or measurements accompany the claim. |

## Findings

1. **Source facts, load test.** Broker X's median (121 ms) is 3 ms higher than the current queue's (118 ms). The test controls hardware and job mix and uses repeated runs (L1). The source states that the 3 ms gap is smaller than the 6 ms spread (L2).
2. **Source facts, vendor note.** The note gives a ceiling ("up to 40 percent") and no baseline, workload, metric or sample. It does not say whether the metric is median latency, and it does not state its own conditions (V1).
3. **Inference.**
   - The load test shows no latency reduction. The point estimate is slightly worse, and the gap is indistinguishable from noise (L1, L2). It therefore does not show that Broker X is slower either.
   - The vendor note cannot offset this. Its claim is unmeasured, its figure is an upper bound, and it comes from customer reports with no method (V1). The two sources do not conflict on measured evidence, because only L1 contains measurements.

## Conclusions and conditions

- **Supported:** In the platform team's test, Broker X did not reduce median latency (L1, L2). This holds only for that hardware and job mix.
- **Unsupported:** The claim that moving to Broker X reduces median job latency. The only controlled measurement does not show it, and the only claim for it carries no evidence (V1).
- **Unresolved, outside the sources:** Whether Broker X would help under other workloads, loads or configurations. The sources do not cover these. The load test does not report a confidence interval, so "no difference" is also not established beyond the stated 6 ms spread.

## Open questions

- Does the real production job mix match the load-test mix?
- What workload and metric underlie the vendor's "40 percent" figure?
- Is a larger or differently designed test warranted, for example one reporting tail latency or confidence intervals?

## Recommended next action

Do not justify the migration on latency grounds with the current evidence. If latency matters to the decision, ask the platform team to rerun the test under production-like load, or ask the vendor for its methodology.

CONCLUSION: UNSUPPORTED
