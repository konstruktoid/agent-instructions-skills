Yes. All three sources show release 4.2 raising the cache hit ratio above 90 percent.

| Source | Setting | Release 4.1 | Release 4.2 |
|---|---|---|---|
| `sources/ops-weekly.md` | Production, week 37 vs week 38, seven days each | 71% | 93% |
| `sources/staging-replay.md` | Same recorded traffic on identical hardware, one hour each | 70% | 92% |
| `sources/canary-log.md` | 10% of production traffic for 24 hours, with a concurrent 4.1 control | 72% | 94% |

- **Production:** `ops-weekly.md` reports 93% in the week after the 4.2 deploy on 2026-09-14, up from 71%. It says the only cache change between the two weeks was the key normalization in 4.2.
- **Staging:** `staging-replay.md` replays the same traffic against both releases. It says the only difference was the release, so it isolates the release effect. The result is 92% for 4.2 against 70% for 4.1.
- **Canary:** `canary-log.md` ran 4.1 and 4.2 side by side, and both groups got the same mix of requests. That controls for time and traffic differences. The result is 94% for 4.2 against 72% for 4.1.

The three sources use different designs: before and after, a controlled replay, and a concurrent control. Each shows 4.2 at 92–94% and 4.1 at 70–72%, a gain of about 21–22 points. The before/after comparison could have been confounded by traffic changes, but the replay and the canary rule that out.

**Where the evidence stops:**
- The sources give no confidence intervals or request counts.
- The replay covers only one hour and the canary only 24 hours. Only the production figure covers a full week.
- The production source credits the gain to the key normalization. The other two sources only show that the release made the difference, and none of them tests the mechanism separately.
- None of the sources says whether the ratio stays above 90% beyond the periods measured.

None of this undermines the claim as asked.

CONCLUSION: SUPPORTED
