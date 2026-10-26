# Evidence report: does Broker X reduce median job latency?

## Evidence inventory

| Source | Location | Material claim | Type |
|---|---|---|---|
| `sources/load-test.md` | lines 3-4 | The platform team ran 20 runs per queue on the same hardware with the same job mix and reported the median. | Method description |
| `sources/load-test.md` | table, lines 5-8 | Median job latency was 118 ms on the current queue and 121 ms on Broker X. | Measurement |
| `sources/load-test.md` | line 10 | The difference is inside the run-to-run spread of 6 ms. | Measurement |
| `sources/vendor-note.md` | lines 3-4 | Customers report that Broker X makes jobs "up to 40 percent faster". | Unattributed testimonial |
| `sources/vendor-note.md` | line 4 | No test setup or measurements accompany the claim. | Source's own limitation |

## Findings

**Agreements.** None. The two sources do not address the same claim with the same rigor.

**Conflict.** The load test shows Broker X at 121 ms against 118 ms for the current queue. That is nominally 3 ms slower, not faster. The vendor note asserts a speedup of up to 40 percent. The two are not directly comparable, for these reasons:
- The load test has a stated method (same hardware, same job mix, 20 runs per queue).
- The vendor note has no method, no baseline, no workload and no named customers.
- "Up to 40 percent" is an upper bound, so it is compatible with a gain of zero.

**Reading the load test.** The 3 ms gap is smaller than the 6 ms run-to-run spread. The test therefore shows no detectable difference in either direction. It gives no evidence of a reduction.

**Reading the vendor note.** It is a marketing claim from the product's own source. The note itself says no measurements accompany it, so it cannot establish a reduction. It also cannot rebut the load test.

## Conclusions and conditions

1. **A median latency reduction from Broker X is not supported.**
   - Basis: `sources/load-test.md` shows no improvement beyond noise, and `sources/vendor-note.md` supplies no measurable evidence.
   - Condition: this holds for the load test's hardware and job mix.
   - Boundary: the sources do not show that Broker X is slower. A 3 ms gap inside a 6 ms spread is not a demonstrated regression.

2. **"No difference" is not established either.** Twenty runs on one workload cannot rule out a small effect, or an effect under a different job mix, load level or hardware. The sources do not say how the spread was computed or which load levels were tested.

3. **The 40 percent figure has no support.** Nothing in the sources links it to any workload, baseline or measurement.

## Open questions

- Do the customers' reported gains come from different job mixes, a higher load or a different baseline queue?
- How was the 6 ms spread defined (range, standard deviation or interquartile range)?
- Was the test run at production concurrency? The note says nothing about queue depth or throughput.
- Do tail latencies (p95 and p99) differ? The sources report only the median.

## Recommended next action

Treat the latency claim as unsupported for decision purposes. If the main conversation still considers Broker X, it could request the vendor's test setup and data, or run a load test at production-like concurrency with a stated statistical method. The platform team would need to run that test, since this report adds no sources.

CONCLUSION: UNSUPPORTED
