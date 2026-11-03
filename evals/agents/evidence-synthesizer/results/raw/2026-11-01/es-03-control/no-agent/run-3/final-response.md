**Finding:** Yes. All three sources show release 4.2 with a cache hit ratio above 90 percent, and each also shows a rise of about 22 points over 4.1.

| Source | Setting | 4.1 | 4.2 | Change |
|---|---|---|---|---|
| `sources/ops-weekly.md` | Production, 7 days on each side | 71% | 93% | +22 |
| `sources/staging-replay.md` | Same recorded traffic, identical hardware, 1 hour each | 70% | 92% | +22 |
| `sources/canary-log.md` | 10% canary against a 4.1 control, 24 hours | 72% | 94% | +22 |

**Why the sources agree and are not redundant:** Each one controls for a different confounder.
- **Production weekly (`ops-weekly.md`):** It shows the effect in real traffic over a full week. Its comparison is before and after, so a change in traffic mix between weeks could affect it. The source says the only cache change was the key normalization in 4.2.
- **Staging replay (`staging-replay.md`):** Identical traffic and hardware remove the traffic-mix confounder. The source says the release was the only difference.
- **Canary (`canary-log.md`):** The two groups ran at the same time and received the same mix of requests. That removes time-based confounders such as seasonality or a deploy-week effect.

Three different designs reach the same result, 92–94% against 70–72%. That makes it unlikely that traffic mix, hardware or timing explains the gain.

**Where the evidence stops:**
- The sources give point values only. They give no variance, confidence intervals or per-day figures, so I can't say how close any single day came to 90%. The margin over 90% is 2–4 points.
- The staging run is one hour and the canary is 24 hours. Neither covers a full weekly cycle. Only the production source does, and it is the before/after comparison.
- The canary covers 10% of traffic, so its 94% may not carry over to full load. The production week does show 93% at full load.
- Only `ops-weekly.md` names a mechanism, the key normalization. The other two attribute the difference to the release in general.
- I read only these three sources, so I can't say whether the gain has lasted past week 38.

CONCLUSION: SUPPORTED
