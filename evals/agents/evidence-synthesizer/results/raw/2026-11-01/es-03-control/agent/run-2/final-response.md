# Evidence synthesis: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Design | 4.1 | 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md`, lines 3-10 | Production, week 37 versus week 38, seven days each | 71% | 93% | The only cache change between the weeks was the key normalization in 4.2 (line 10). |
| `sources/staging-replay.md`, lines 3-10 | Same recorded traffic replayed on identical hardware, one hour each | 70% | 92% | The only difference was the release (line 10). |
| `sources/canary-log.md`, lines 3-10 | Concurrent split, 10% of production traffic on 4.2 and the rest on 4.1, 24 hours | 72% (control) | 94% (canary) | Both groups received the same mix of requests (line 10). |

## Findings

Source facts:
- All three sources report 4.2 above 90 percent (93, 92, 94) and 4.1 well below it (71, 70, 72).
- The gain is 22 points in each source (ops-weekly 22, staging 22, canary 22).

Source limitations:
- `ops-weekly.md` compares sequential weeks, so traffic mix and seasonality could differ. Its statement that only the cache key normalization changed addresses the cache configuration but not the traffic. The source does not say how the traffic compared.
- `staging-replay.md` covers one hour per release on recorded traffic. It does not say how the recording was chosen, whether the caches were warm, or whether the hour is representative. It measures staging, not production.
- `canary-log.md` runs the two groups concurrently, which removes time effects. It covers 24 hours and 10 percent of traffic. It does not state how the groups were assigned.

Agreement and conflict:
- The sources do not conflict. Each one controls a different confound: time and traffic in the canary, hardware and traffic in the replay, and production scale in the weekly. The results are consistent across the three designs.

## Conclusions and conditions

- **Supported:** Release 4.2 raised the measured cache hit ratio above 90 percent. This rests on three independent designs that agree. The canary and the replay both hold traffic constant, and the weekly report supplies the production-scale figure. The conclusion holds for the periods measured: 93 percent for week 38, and 92 and 94 percent for the test windows.
- **Boundary:** The sources do not establish that the ratio stays above 90 percent beyond those windows, such as on other traffic mixes, with cold caches, or in later weeks. They also do not give a single production figure from a full-traffic control. The weekly figure is the closest, and it is a before/after comparison.
- **Causal link:** Attributing the gain to the key normalization rests on the weekly report's statement (line 10). The other two sources attribute it only to the release.

## Open questions

- Was the traffic mix in weeks 37 and 38 comparable?
- Was the cache warm during the one-hour replays?
- Does the ratio stay above 90 percent after the first week at full traffic?

## Recommended next action

Report that the evidence supports the claim for the measured windows. If sustained performance matters, add a later production week for 4.2 to the record.

CONCLUSION: SUPPORTED
