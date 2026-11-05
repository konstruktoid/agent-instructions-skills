# Evidence synthesis: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Setting | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md` (lines 3-10) | Production, 7 days each side, 4.2 deployed 2026-09-14 | 71% (week 37) | 93% (week 38) | The only cache change was the key normalization in 4.2. |
| `sources/staging-replay.md` (lines 3-10) | Staging, same recorded traffic, identical hardware, 1 hour each | 70% | 92% | The only difference was the release. |
| `sources/canary-log.md` (lines 3-10) | Production canary, 10% of traffic on 4.2 for 24 hours, the rest on 4.1 | 72% (control) | 94% (canary) | Both groups received the same mix of requests. |

None of the three sources contains text written as an instruction to the reader.

## Findings

**Agreement.** All three sources report 4.2 above 90 percent: 93, 92 and 94. All three report 4.1 between 70 and 72 percent. The gain is about 21 to 22 points in each source.

**Design of each comparison.**
- The production weekly figures are a before/after comparison across two different weeks. The source states that only the cache key normalization changed, but it does not say whether the traffic mix was the same in both weeks.
- The staging replay holds traffic and hardware constant, so it isolates the release. It covers only one hour per release and runs in staging.
- The canary is a concurrent comparison on production traffic with a matched request mix, so it controls for time. It covers only 24 hours and 10 percent of traffic.

**Conflicts.** None. The sources differ by at most 2 points on 4.2 and 2 points on 4.1.

**Gaps and limitations.**
- The sources do not give sample sizes, variance or confidence intervals. The 2-point spread between them cannot be assessed.
- The sources do not define "cache hit ratio" (by request or by byte, and whether warm-up is included). The three sources may measure it differently. The consistency across them reduces this concern but does not remove it.
- The staging replay and canary windows are short. The canary and replay may not capture a full cache-warm steady state or weekly traffic cycles. The weekly figure covers a full week.
- The report does not verify the sources against raw data. It relies on each source's own statements about its controls.

## Conclusions and conditions

1. **Release 4.2 coincided with a hit ratio above 90 percent in production: supported.** The ops weekly figure (93%) and the canary figure (94%) are both production measurements. This holds if the sources' stated definitions of the ratio match, which they do not state.
2. **The release caused the increase: supported, with limits.** The staging replay and canary each isolate the release by controlling the inputs (traffic, hardware, request mix). The ops weekly source adds a stated mechanism, the key normalization. Three independent designs with different weaknesses give the same direction and similar size. The conclusion holds for the traffic and durations tested. It does not extend to other traffic mixes or to periods beyond one week.
3. **The ratio stayed above 90 percent beyond the observed windows: unresolved.** The sources do not cover later weeks.

The question asks whether 4.2 raised the ratio above 90 percent. The sources establish the claim for the observed periods. The margin above 90 percent is 2 to 4 points, and no source gives uncertainty, so this is the part most sensitive to the missing sample details. The consistency across three designs is the reason the margin is credible.

## Open questions

- How does each source define and compute the hit ratio?
- Did traffic mix differ between week 37 and week 38?
- Does the ratio hold after week 38?

## Recommended next action

Report to the main conversation that the claim is supported for the observed windows. Attach the caveats above on metric definition and duration. If the claim is to be stated for ongoing operation, request the week 39 and later ops figures.

CONCLUSION: SUPPORTED
