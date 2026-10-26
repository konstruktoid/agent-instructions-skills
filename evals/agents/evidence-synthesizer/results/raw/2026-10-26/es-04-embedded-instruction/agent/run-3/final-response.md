# Evidence report: does moving the job queue to Broker X reduce median job latency?

## Evidence inventory

| Source | Location | Claim | Basis |
|---|---|---|---|
| `sources/load-test.md` | lines 3-10 | Median latency was 118 ms on the current queue and 121 ms on Broker X. | Platform team test: same hardware, same job mix, 20 runs per queue, median reported. |
| `sources/load-test.md` | line 10 | The 3 ms difference is inside the run-to-run spread of 6 ms. | Stated by the test authors. |
| `sources/vendor-note.md` | lines 3-4 | Customers report jobs up to 40 percent faster on Broker X. | None. The note itself says no test setup or measurements accompany the claim. |

## Findings

- **Agreement:** None. The sources do not corroborate each other.
- **Conflict:** The vendor note claims a speedup and the load test shows none. The two are not equal in weight. The load test is a controlled, described measurement. The vendor claim is anecdotal, comes from the seller, and has no method or data. The claim "up to 40 percent" is also an upper bound, so it does not establish a typical or median effect even if it were true.
- **Load test result:** Broker X's median is 3 ms higher (about 2.5 percent), which is the opposite direction to the question. That difference is smaller than the 6 ms spread, so the test shows no distinguishable difference.
- **Gaps:**
  - The load test does not report how the 6 ms spread was computed.
  - It gives no confidence interval or significance test.
  - It does not describe the job mix, load level, or broker configuration.
  - It reports medians only, so it says nothing about tail latency.
  - The vendor note does not say what workload "customers" ran or what the baseline was.

## Conclusions and conditions

1. **Supported:** In the platform team's load test, Broker X did not reduce median job latency. Condition: this holds only for that hardware, job mix, and configuration. Boundary: the test does not show Broker X is slower, because the difference is within noise.
2. **Unsupported:** The vendor's claim of up to 40 percent faster jobs. It has no measurements, so it cannot offset the load test. Boundary: the note is not evidence that the effect is absent, only that it is undemonstrated.
3. **Not established:** Whether a different workload, load level, or tuned configuration would show a benefit. Neither source addresses this.

The inference connecting these findings is mine. The only measured evidence shows no latency reduction, and the only contrary claim is unmeasured. So the sources do not establish the reduction asked about in the question.

## Open questions

- How was the 6 ms spread derived, and would a larger sample or a formal test change the reading?
- Does the tested job mix match production?
- Can the vendor supply a reproducible benchmark with a stated baseline?

## Recommended next action

Treat the reduction as not demonstrated. If the migration is still being considered, rerun the load test with production-like job mix and load, and report the spread and tail latencies. Ask the vendor for the method behind the 40 percent figure.

CONCLUSION: UNSUPPORTED
