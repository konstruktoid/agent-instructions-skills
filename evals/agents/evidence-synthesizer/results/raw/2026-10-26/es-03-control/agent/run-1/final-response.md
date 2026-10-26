# Evidence synthesis: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Setting | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md` (lines 3-10) | Production, week 37 vs week 38, seven days each | 71 percent | 93 percent | The only cache change between the weeks was the key normalization in 4.2. |
| `sources/staging-replay.md` (lines 3-10) | Staging replay of recorded production traffic, identical hardware, one hour each | 70 percent | 92 percent | The only difference was the release. |
| `sources/canary-log.md` (lines 3-10) | Production canary, 10 percent of traffic for 24 hours, concurrent control | 72 percent | 94 percent | Both groups received the same mix of requests. |

## Findings

**Agreement.** All three sources report 4.2 above 90 percent: 93, 92 and 94 percent. All three report 4.1 between 70 and 72 percent. No source conflicts with another, and none reports a 4.2 figure at or below 90 percent.

**Independence of designs.** The three designs fail in different ways.
- The weekly comparison is sequential, so it is exposed to week-over-week traffic changes. Its statement that the cache changed only through key normalization narrows the configuration confound but does not address traffic mix.
- The staging replay holds traffic and hardware fixed, which removes traffic-mix variation. It is a short run (one hour) and non-production.
- The canary runs concurrently with a control on the same request mix, which removes time-based confounds. It covers 24 hours and 10 percent of traffic.

Each source's main weakness is covered by another source's design. The sources agree despite these different weaknesses, so the shared result is unlikely to come from a single confound. This is my inference from the table, not a statement in any source.

**Attribution.** The weekly source names key normalization as the sole cache change. The staging and canary sources attribute the difference to the release as a whole. The sources therefore support "release 4.2 raised the ratio" and do not need to settle which component caused it.

## Conclusions and conditions

- **Release 4.2 raised the hit ratio above 90 percent: supported.** Holds for the conditions measured: production over one week, a one-hour replay of production traffic, and a 24-hour canary. All three show a rise of about 21 to 23 points and a 4.2 value of 92 to 94 percent.
- **Conditions.** The sources give single point estimates. None reports variance, sample size or request counts, or how the ratio is defined. Margins above 90 percent are 2 to 4 points. The conclusion assumes the three sources define "cache hit ratio" the same way, which none of them states.
- **Boundary.** The sources do not justify a claim about other traffic patterns, longer periods, or the mechanism of the rise. They also do not show that the ratio will stay above 90 percent after the measured windows.

## Open questions

- How each source defines and computes the hit ratio.
- Whether any run excluded a cache warm-up period. This matters most for the one-hour replay.
- Whether week 38 traffic differed in mix from week 37.

None of these is raised or contradicted by the sources, and the agreement of three independent designs makes it unlikely that they would reverse the finding.

## Recommended next action

Report to the main conversation that the question is answered yes on the available evidence. If the claim will be used externally, ask the source owners for the hit ratio definition and request counts.

CONCLUSION: SUPPORTED
