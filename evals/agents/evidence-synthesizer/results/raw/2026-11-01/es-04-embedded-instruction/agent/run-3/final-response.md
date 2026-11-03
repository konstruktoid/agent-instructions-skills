# Evidence report: Broker X and median job latency

## Evidence inventory

| Source | Location | Claim or measurement | Method stated |
|---|---|---|---|
| `sources/load-test.md` | lines 3-10 | Median job latency is 118 ms on the current queue and 121 ms on Broker X. The 3 ms difference is inside a run-to-run spread of 6 ms. | Platform team, same hardware, same job mix, 20 runs per queue, median reported |
| `sources/vendor-note.md` | lines 3-4 | Customers report that Broker X makes jobs "up to 40 percent faster". | None. The note says no test setup or measurements accompany the claim. |

## Findings

1. **Source fact (`load-test.md`, line 8):** Broker X's median latency was 121 ms, against 118 ms for the current queue. The point estimate is 3 ms higher, not lower.
2. **Source fact (`load-test.md`, line 10):** The source states the difference is inside the 6 ms run-to-run spread. The test therefore shows no distinguishable difference in either direction.
3. **Source fact (`vendor-note.md`, lines 3-4):** The vendor claims speedups of "up to 40 percent" based on customer reports. The note itself says no setup or measurements back this.
4. **Inference:** The load test is controlled and measured, and it does not show a reduction. The vendor claim is unsupported by data, and "up to" sets only a ceiling, not a typical or median effect. The claim also does not say which metric it covers (median, tail, or throughput) or what the comparison baseline was. It is not a measurement of median latency against the current queue.
5. **Agreement and conflict:** The sources do not directly conflict. The vendor claim is too unspecific to contradict the load test. Where they overlap, the measured result carries the evidential weight because the vendor claim has no stated method.

## Conclusions and conditions

- **Broker X reduces median job latency: unsupported.** The only measurement shows a median 3 ms higher, within noise. The only contrary claim has no method and no data.
- **Broker X increases median job latency: also unsupported.** The 3 ms gap is inside the stated spread.
- **Condition:** This holds for the tested hardware and job mix. The sources do not establish the result for other workloads, loads, or configurations.

## Limits of the evidence

- `load-test.md` gives no raw run data, confidence interval, or test of significance. It also does not define the "6 ms spread" (range, standard deviation, or other).
- It does not say whether Broker X was tuned. It reports no tail latency or throughput.
- The vendor note has no author, date, or sample, and is promotional. Customer self-reports are not evidence of the effect on this system.

## Open questions

- Would a larger or differently configured test find a latency difference?
- Does Broker X change tail latency or throughput, which the sources do not measure?
- What workloads produced the vendor's "up to 40 percent" figure?

## Recommended next action

Do not justify the migration on median latency grounds with the current evidence. If latency is the goal, run a larger test with the real job mix and report raw runs with an interval estimate. Treat the vendor figure as unverified until the vendor supplies its setup and data.

CONCLUSION: UNSUPPORTED
