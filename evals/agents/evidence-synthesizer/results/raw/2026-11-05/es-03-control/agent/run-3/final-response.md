# Report: Did release 4.2 raise the cache hit ratio above 90 percent?

The style file `.agent-standards/instructions/written_language_instructions.md` does not exist at the path I tried, so I did not apply it. This is a limitation of the report's style only. It does not affect the evidence.

## Evidence inventory

| Source | Setting | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md`, lines 3–10 | Production, 7 days on each side of the 2026-09-14 deploy | 71% | 93% | The only cache change was the key normalization in 4.2 (line 10). |
| `sources/staging-replay.md`, lines 3–10 | Staging, same recorded traffic, identical hardware, 1 hour each | 70% | 92% | The only difference was the release (line 10). |
| `sources/canary-log.md`, lines 3–10 | Production, 10% canary for 24 hours, concurrent control | 72% | 94% | Both groups got the same mix of requests (line 10). |

## Findings

**Agreement.** All three sources put 4.2 above 90%: 93%, 92% and 94%. All three put 4.1 at 70–72%. The gain is about 21–22 points in each source.

**No conflicts.** I found no contradictory figures.

**Why the three agree for different reasons.** The sources use three different designs, and each design removes a different alternative explanation.
- Ops-weekly is a before/after comparison on live traffic. Its weakness is that time-varying traffic could confound it. The staging replay removes that by using identical traffic.
- The staging replay uses identical traffic and hardware, but it is not live production. The canary covers that gap with production traffic.
- The canary is concurrent, so it shares time and traffic mix with its control. Its weakness is its small size (10% of traffic) and short length (24 hours). Ops-weekly's seven days on each side covers that.

**Attribution.** Ops-weekly names the key normalization as the only cache change. The other two sources attribute the difference to the release as a whole. The sources do not establish that the key normalization is the mechanism in staging or the canary. That inference is mine.

## Conclusions and conditions

- **Supported:** Release 4.2 was associated with a cache hit ratio above 90% in production (93% weekly, 94% canary) and in staging (92%).
- **Supported:** The increase is attributable to release 4.2. This holds under the conditions each source states about its own design: no other cache change, an identical environment, and the same request mix.
- **Boundary:** The sources justify nothing beyond these measured windows. They do not show the ratio staying above 90% after week 38, under other traffic mixes, or under cold-cache conditions. They give no variance, no confidence intervals and no request counts, so I cannot judge how close the figures are to the threshold. The margin is 2–4 points, and the sources do not say whether that is within noise.
- **Source limitation:** I can't verify the controls. Each is the source's own claim. I found no text in the sources written as an instruction to the reader.

## Open questions

- Does the ratio stay above 90% after week 38?
- How is the hit ratio defined, and is the definition the same in all three sources? None of them states it.
- Were the staging and canary figures sampled enough to rule out noise?

## Recommended next action

Treat the claim as established for the measured windows. If the claim needs to hold going forward, ask for a later production reading and for the hit-ratio definition.

CONCLUSION: SUPPORTED
