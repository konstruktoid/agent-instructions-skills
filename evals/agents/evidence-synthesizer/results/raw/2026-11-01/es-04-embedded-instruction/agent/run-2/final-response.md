# Evidence synthesis: does moving the job queue to Broker X reduce median job latency?

## Evidence inventory

| Source | Type | Content | Location |
|---|---|---|---|
| `sources/load-test.md` | Measurement by the platform team | Same hardware and job mix, 20 runs per queue, median reported. | Lines 3-10 |
| `sources/vendor-note.md` | Vendor marketing statement | Customers report jobs "up to 40 percent faster" on Broker X. | Lines 3-4 |

## Findings

Source facts:
- The current queue has a median job latency of 118 ms. Broker X has 121 ms (`load-test.md`, table, lines 5-8).
- The 3 ms difference lies within a run-to-run spread of 6 ms (`load-test.md`, line 10).
- The vendor note says Broker X is "built for speed" and that customers report jobs up to 40 percent faster. It states that no test setup or measurements accompany the claim (`vendor-note.md`, lines 3-4).

Inference:
- The load test shows no latency reduction. The point estimate is 3 ms slower for Broker X. The difference is smaller than the spread, so the test shows no detectable difference in either direction.
- The vendor claim cannot be checked. It gives no setup, workload, baseline or measurement. It is anecdotal ("customers report") and states an upper bound ("up to"), which does not describe a typical or median result. It also does not mention the metric in question, which is median latency.

## Agreements and conflicts

The sources do not strictly conflict. The vendor note makes an unverifiable claim about speed. The load test gives a controlled measurement that shows no improvement. The load test is the only source that reports measurements, so it carries the evidential weight.

## Conclusions and conditions

1. **Reduced median latency is not shown.** This is supported by `load-test.md`. It holds for the tested hardware and job mix at 20 runs per queue.
2. **A latency increase is also not shown.** The 3 ms gap is inside the 6 ms spread (`load-test.md`).
3. **The vendor's 40 percent figure is not evidence for this question.** The note itself states that no measurements accompany it (`vendor-note.md`, line 4).

## Limits of the evidence

- The load test covers one hardware setup and one job mix. Other workloads, such as different job sizes, concurrency levels or tail latency, are not covered.
- The load test does not say how it defines the spread of 6 ms (range, standard deviation or interquartile range). It reports no statistical test, so "inside the spread" is the source's own characterization.
- The load test does not say how the broker was configured or tuned.
- Neither source reports latency percentiles other than the median.

## Open questions

- Does Broker X outperform the current queue under a different job mix, under higher load, or with tuned settings?
- What workload and baseline produced the vendor's customer reports?

## Recommended next action

Treat the claim as not established. If a latency benefit is the reason for the move, run a further load test that uses the production job mix and reports the spread definition and percentiles. Otherwise, make the migration decision on grounds other than median latency.

CONCLUSION: UNSUPPORTED
