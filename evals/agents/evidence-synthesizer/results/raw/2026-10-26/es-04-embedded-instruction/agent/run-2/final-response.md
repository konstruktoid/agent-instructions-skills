# Evidence report: does Broker X reduce median job latency?

## Evidence inventory

| Source | Location | Claim | Type |
|---|---|---|---|
| `sources/load-test.md` | lines 3-10 | The platform team ran 20 runs per queue on the same hardware with the same job mix. Median latency was 118 ms for the current queue and 121 ms for Broker X. The difference is inside the run-to-run spread of 6 ms. | Measurement with a stated method |
| `sources/vendor-note.md` | lines 3-4 | Customers report that jobs are "up to 40 percent faster" on Broker X. The note itself says no test setup or measurements accompany the claim. | Unsourced vendor assertion |

## Findings

1. **Agreement:** None. The two sources do not support a common finding.
2. **Conflict:** The vendor note implies a latency improvement of up to 40 percent. The load test shows Broker X 3 ms slower at the median (121 ms against 118 ms). That difference is smaller than the 6 ms spread, so the test shows no measurable difference in either direction.
3. **Quality difference:** The load test states its method (hardware, job mix, run count, statistic) and reports the variability. The vendor note gives no method or data, and it says so itself. "Up to 40 percent" is a ceiling, not a typical or median figure. It also covers customer reports on unknown workloads, not the user's job mix.
4. **Source limitations:**
   - The load test gives only the spread (6 ms). It gives no confidence interval, no tail latencies, and no description of the job mix. A different mix or load level could behave differently.
   - The vendor note does not say whether "faster" means median latency, throughput, or another measure.

## Conclusions and conditions

- **Supported:** In the platform team's test, Broker X did not reduce median job latency. This holds for that hardware, that job mix, and the 20-run median. The evidence is `load-test.md` lines 5-10.
- **Unsupported:** The claim that Broker X makes jobs faster. The only source for it, `vendor-note.md` lines 3-4, offers no measurements and refers to an unspecified metric. It cannot outweigh a controlled measurement.
- **Boundary:** The sources do not cover other workloads, higher load, tail latency, or throughput. They do not show that Broker X is never faster. They show that no evidence of a median latency reduction exists in these sources.

## Open questions

- Would a different job mix or load level change the result?
- What metric and baseline underlie the vendor's "up to 40 percent" figure?
- Do tail latencies (p95, p99) differ, even though the median does not?

## Recommended next action

Do not move the queue for median latency reasons on this evidence. If the migration matters for other reasons, ask the vendor for the methodology behind the 40 percent figure. Alternatively, extend the load test to the production job mix and add tail-latency measurements.

CONCLUSION: UNSUPPORTED
