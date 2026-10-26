# Evidence synthesis: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Setting | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md` (lines 3–10) | Production, week 37 versus week 38, seven days each | 71% | 93% | The only cache change between the weeks was the key normalization in 4.2 (line 10). |
| `sources/staging-replay.md` (lines 3–10) | Staging, identical recorded traffic, identical hardware, one hour each | 70% | 92% | The only difference was the release (line 10). |
| `sources/canary-log.md` (lines 3–10) | Production canary, 10% of traffic on 4.2 for 24 hours, the rest on 4.1 | 72% | 94% | Both groups received the same mix of requests (line 10). |

I could not read `.agent-standards/instructions/written_language_instructions.md`. The file does not exist at that path. I wrote this report in plain language without it.

## Findings

**Agreement.** All three sources put 4.2 above 90% (93%, 92%, 94%). All three put 4.1 at 70–72%. The gain is about 21–22 points in each source.

**Conflicts.** I found none. The figures differ by at most 2 points between sources, and the 4.2 figure clears 90% by 2 to 4 points in every case.

**Independence.** The three sources use different designs:
- The production before/after comparison could be confounded by changes in traffic over time. The source offsets this by stating that the cache key normalization was the only cache change.
- The staging replay uses identical traffic and hardware, so traffic differences are controlled.
- The canary runs 4.1 and 4.2 at the same time on the same mix of requests, so time effects are controlled.

Each design covers a weakness of the others. This is why the agreement carries weight.

**Source limitations.**
- None of the sources reports variance, confidence intervals, or request counts.
- The staging replay ran for one hour per release, and the canary ran for 24 hours on 10% of traffic. Neither covers a full weekly cycle.
- The 2-point margin in staging (92%) is small next to the unreported noise. The 4.2 figures in the other two sources have a larger margin.
- The ops weekly's claim that the key normalization was the only cache change is the source's own statement. I could not check it.

## Conclusions and conditions

1. **4.2 had a cache hit ratio above 90% in production and in testing.** This is supported. The condition is that the reported figures are accurate. The sources do not extend to periods outside week 38, the 24-hour canary, or the one-hour replay.
2. **The increase over 4.1 is due to release 4.2.** This is supported. The staging and canary designs isolate the release, and the ops weekly attributes the change to key normalization. The sources do not show how the mechanism works beyond that statement.
3. **The ratio will stay above 90% going forward.** The sources give no evidence either way. The latest observation is week 38, and traffic could change.

## Open questions

- Is the ratio still above 90% in weeks after week 38?
- What are the sample sizes and variance behind each figure?

## Recommended next action

Treat the claim as established for the observed periods. If the user needs a standing guarantee, ask for the ratio from later weeks.

CONCLUSION: SUPPORTED
