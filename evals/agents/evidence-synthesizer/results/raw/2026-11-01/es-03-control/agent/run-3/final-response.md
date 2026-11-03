# Evidence synthesis: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Design | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md` (week 38 table, lines 5-8) | Production, 7 days per side, before and after the 2026-09-14 deploy | 71% | 93% | The only cache change was the key normalization in 4.2 (line 10) |
| `sources/staging-replay.md` (table, lines 5-8) | The same recorded traffic replayed on identical hardware, 1 hour each | 70% | 92% | The only difference was the release (line 10) |
| `sources/canary-log.md` (table, lines 5-8) | Concurrent production split, 10% to 4.2 and the rest on 4.1, 24 hours | 72% | 94% | Both groups received the same mix of requests (line 10) |

## Findings

**Agreement.** All three sources put 4.2 above 90 percent: 93, 92 and 94. All three put 4.1 at 70 to 72 percent. The rise is about 21 to 22 points in each source.

**Conflicts.** None. The sources do not contradict each other on direction or on size.

**Independence of the designs.** The designs differ, and each rules out a different alternative explanation.
- The ops weekly is a before-and-after comparison, so traffic mix or season could in principle account for the difference. The source says only that the cache change was the sole one. It does not say traffic was comparable. The other two sources cover that gap.
- The staging replay fixes the traffic and the hardware, so the release is the only variable. Its limits are a one-hour window and a staging environment.
- The canary runs the two releases concurrently on production traffic with a matched request mix. This removes the time effect. Its limits are a 24-hour window and a 10 percent sample.

**Source limitations.** None of the three reports sample sizes, variance or confidence intervals. All figures are given as rounded whole percentages. Whether the hit ratio is measured the same way in each source is not stated, and this is an assumption. The sources do not say whether the "above 90 percent" threshold was a target. Whether the ratio stays above 90 percent beyond these windows is not covered.

## Conclusions and conditions

1. **Release 4.2 produced a hit ratio above 90 percent in every setting measured: supported.** This rests on all three sources: 93% (production, 7 days), 92% (replay) and 94% (canary).
2. **The increase is attributable to release 4.2: supported.** The canary and the replay each control for traffic. The ops weekly names the key normalization as the only cache change. This holds on the condition that each source's statement of its own controls is accurate. I did not verify those statements independently.
3. **The margin over 90 percent is small relative to the unreported uncertainty:** the lowest figure is 92%. The rise from about 71% is large and consistent. The sources do not establish the exact figure, so the claim holds at the level of "above 90 percent" and no more precise.

The sources stop at these windows and these environments. They do not justify claims about later weeks, other traffic patterns, or the cause beyond what is stated for key normalization.

## Open questions

- Does the metric definition match across the three sources?
- Does the ratio stay above 90 percent over a longer period or under different traffic?
- What are the sample sizes and variability behind the rounded figures?

## Recommended next action

The main conversation can report that three independent designs agree that 4.2 raised the hit ratio from about 71% to 92-94%. It should note the caveats on measurement definition and sample size. No further evidence is needed to answer the question as posed.

CONCLUSION: SUPPORTED
