# Evidence report: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Setting | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md` (lines 3-10) | Production, week 37 vs week 38, seven days each | 71% | 93% | The only cache change between the weeks was the key normalization in 4.2. |
| `sources/staging-replay.md` (lines 3-10) | Staging, same recorded production traffic, identical hardware, one hour each | 70% | 92% | The only difference between the deployments was the release. |
| `sources/canary-log.md` (lines 3-10) | Production canary, 10% of traffic on 4.2 for 24 hours, concurrent control on 4.1 | 72% | 94% | Both groups received the same mix of requests. |

## Findings

**Agreement.** All three sources report a 4.2 hit ratio above 90 percent (93, 92, 94). All three report a 4.1 baseline of 70 to 72 percent. The size of the increase is consistent: 22, 22 and 22 points.

**Independence of designs.** Each source controls a different threat to validity.
- The weekly comparison is before and after. Time-varying traffic could confound it. The source rules out other cache changes but not traffic differences between the weeks.
- The staging replay holds traffic and hardware fixed. It covers one hour, and staging may differ from production.
- The canary runs 4.1 and 4.2 concurrently in production, so time-varying traffic affects both groups equally. It covers 24 hours, and only 10% of traffic went to 4.2.

The confound in one design is addressed by another. The weekly design is exposed to traffic change, and the canary and the replay hold traffic constant.

**Conflicts.** None. No source reports a 4.2 figure at or below 90 percent. No source disputes another.

**Gaps and limitations.**
- No source gives sample sizes, request counts, variance or confidence intervals. The 24-hour and one-hour windows are short, and the figures are single point values.
- The ratios are stated as whole percentages with no definition of "hit ratio" (for example, whether it is per request or per byte). The sources do not say whether the definition is the same across them.
- The canary's 10% slice may have a smaller or warmer cache than a full rollout. The sources do not address this.
- Each source states its control claim itself. I did not verify these claims independently.

## Conclusions and conditions

1. **Release 4.2 produced a hit ratio above 90 percent in each tested setting: supported.** This follows from the three reported figures (93, 92, 94 percent), in production over a week, in a traffic replay, and in a concurrent canary.
2. **The increase is attributable to release 4.2: supported, on the sources' own control statements.** The canary and the replay each isolate the release, and the weekly report attributes the change to key normalization. This holds if the stated controls are accurate and the hit ratio is defined the same way in each source.
3. **The result will hold at 90 percent or higher beyond the observed windows: not established.** The sources give no data on longer periods, other traffic mixes, or variance. The margins above 90 percent are 2 to 4 points, with no uncertainty estimate. The sources do not justify a claim about the future.

## Open questions

- How is the hit ratio defined and measured in each source?
- What are the request counts and variance behind each figure?
- Does the ratio stay above 90 percent after full rollout, beyond the first production week?

## Recommended next action

Report to the main conversation that three independent designs agree that 4.2 raised the ratio above 90 percent. State that the sources give no uncertainty estimates. If the answer will support a threshold commitment, request request counts and the metric definition.

CONCLUSION: SUPPORTED
