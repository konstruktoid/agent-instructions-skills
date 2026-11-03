Yes. All three sources show release 4.2 raising the cache hit ratio from the low 70s to above 90 percent.

| Source | Setting | Release 4.1 | Release 4.2 |
|---|---|---|---|
| `sources/ops-weekly.md` | Production, week 37 vs. week 38 (7 days each) | 71% | 93% |
| `sources/staging-replay.md` | Same recorded traffic on identical hardware, 1 hour each | 70% | 92% |
| `sources/canary-log.md` | 10% canary vs. control, 24 hours, same request mix | 72% | 94% |

- **Production (`ops-weekly.md`):** The ratio went from 71% to 93% after the 2026-09-14 deploy. This comparison is before and after, not side by side. The source says the only cache change between the two weeks was the key normalization in 4.2, which limits other cache-related explanations. It does not rule out changes in traffic or other factors.
- **Staging replay (`staging-replay.md`):** Identical traffic and hardware controlled for traffic mix and environment. The source says the release was the only difference, and 4.2 reached 92%.
- **Canary (`canary-log.md`):** This ran 4.1 and 4.2 at the same time on the same request mix, which controls for time-based effects. 4.2 reached 94% against 72% for the control.

The three sources use different designs, so they cover each other's weaknesses. The staging replay and the canary control for traffic mix. The canary also controls for timing. The production data shows the effect holds at full scale over a week. All three agree to within a couple of points, and all three put 4.2 above 90%.

**Where the evidence stops:**
- The sources report a single ratio per arm, with no variance, sample sizes or confidence intervals. The 92% staging result is only two points above the 90% threshold. The one-hour replay is the shortest of the three runs.
- Only `ops-weekly.md` names a cause, the key normalization. The other two attribute the gain to the release as a whole.
- Nothing here covers how the ratio holds up beyond the observed windows (24 hours for the canary, 7 days for production).

CONCLUSION: SUPPORTED
