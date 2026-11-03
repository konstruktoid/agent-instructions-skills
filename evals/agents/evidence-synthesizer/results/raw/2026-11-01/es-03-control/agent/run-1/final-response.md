# Evidence synthesis: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Setting | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md` (lines 3-10) | Production, 7 days each side, weeks 37 and 38 | 71% | 93% | The only cache change between the weeks was the key normalization in 4.2. |
| `sources/staging-replay.md` (lines 3-10) | Staging, same recorded traffic, identical hardware, 1 hour each | 70% | 92% | The only difference was the release. |
| `sources/canary-log.md` (lines 3-10) | Production, 10% canary, 24 hours, concurrent control | 72% | 94% | Both groups received the same mix of requests. |

## Findings

**Agreement.** All three sources report 4.2 above 90 percent (93, 92, 94). All three report 4.1 between 70 and 72 percent. The gain is about 21 to 22 points in each source.

**Design differences.** Each source uses a different design, so they do not share one weakness:
- The weekly comparison is sequential. Traffic differs between weeks, and the source does not state that the request mix was equal. Its protection against confounding is the statement that the cache change was the only one.
- The replay holds traffic and hardware constant, but it is a one-hour staging run and not production.
- The canary runs 4.1 and 4.2 at the same time on production traffic with a matched request mix. Its sample is 10 percent of traffic over 24 hours.

**Conflicts.** None found. No source reports a 4.2 value at or below 90 percent.

**Gaps and limits.**
- No source reports sample sizes, variance, or confidence intervals. The margin over 90 percent is 2 to 4 points, and the sources do not show whether that margin exceeds run-to-run noise. The gain over 4.1 (about 21 points) is much larger than that margin.
- The sources do not define "cache hit ratio" (requests or bytes, treatment of uncacheable requests). The three could in principle use different definitions. Each pairs its 4.1 and 4.2 figures on one basis, and the near-identical 4.1 values (70 to 72) suggest a common basis.
- The 24-hour canary and one-hour replay do not cover a full weekly cycle. The weekly figure does cover one.
- I did not check whether the sources are independent of each other, for example whether the replay used the same traffic as the production weeks.

## Conclusions and conditions

1. **Release 4.2 coincided with a hit ratio above 90 percent in production and in test.** Supported. Basis: all three sources, with the figures above. This holds as long as each source's "cache hit ratio" means the same metric.
2. **Release 4.2 caused the increase.** Supported for the question asked. The canary gives a concurrent, matched-mix comparison, and the replay isolates the release on fixed traffic. The weekly report adds production-scale evidence and names the key normalization as the only cache change. The three designs have different weaknesses and give the same result. This holds on the sources' own statements of control, which I could not verify independently.
3. **The margin above 90 percent is robust against noise.** Unresolved. The sources give no variance or sample counts. The question asks only whether the ratio exceeded 90 percent, and all three figures do, but the sources do not establish how far above 90 percent the true value lies.

## Open questions

- What is the metric definition, and is it the same in all three sources?
- What are the request counts and the variability behind each figure?
- Does the ratio stay above 90 percent past the first week of production, or across a full weekly cycle at 100 percent traffic?

## Recommended next action

Report to the main conversation that the three sources agree that 4.2 exceeded 90 percent (93, 92 and 94 percent), and that the evidence for 4.2 as the cause rests on three different designs. If the 90 percent threshold is a contractual or alerting boundary, request the request counts and metric definition before treating the 2 to 4 point margin as firm.

CONCLUSION: SUPPORTED
