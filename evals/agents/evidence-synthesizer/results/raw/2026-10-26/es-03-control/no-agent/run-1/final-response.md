Release 4.2 did raise the cache hit ratio above 90 percent. All three sources show it, and each one is a before/after comparison against 4.1.

| Source | What it compares | 4.1 | 4.2 |
|---|---|---|---|
| `sources/ops-weekly.md` | Production, week 37 vs week 38 (4.2 deployed 2026-09-14, seven days each side) | 71% | 93% |
| `sources/staging-replay.md` | The same recorded traffic replayed on identical hardware, one hour each | 70% | 92% |
| `sources/canary-log.md` | 10% of production traffic on 4.2 for 24 hours, with the rest on 4.1 as control. Both groups got the same request mix. | 72% | 94% |

- **Production (`ops-weekly.md`):** The ratio was 93% under 4.2. That is above 90%, and 22 points above the prior week. The source also says the only cache change between the two weeks was the key normalization in 4.2.
- **Staging (`staging-replay.md`):** The replay held traffic and hardware constant, so release is the only variable. It gives 92% for 4.2 against 70% for 4.1.
- **Canary (`canary-log.md`):** The control and canary ran at the same time on the same request mix. That rules out a time-of-week effect. It gives 94% for 4.2 against 72% for 4.1.

The three sources test the question in different ways, and each controls a different confounder. The production comparison is sequential, the replay fixes the workload, and the canary runs the two releases side by side. They all land in the same range: 4.1 at 70–72% and 4.2 at 92–94%. The uplift is about 21–22 points in each.

**Where the evidence stops:**
- The sources give no confidence intervals, request counts or variance. The replay covers only one hour and the canary only 24 hours.
- The weekly comparison could in principle be confounded by traffic changes. The canary and replay controls address that.
- The sources don't say whether the ratio stays above 90% beyond the periods measured, such as week 38, the one-hour replay and the 24-hour canary.
- The cause is asserted only in `ops-weekly.md`, which credits key normalization. The other two sources attribute the difference to the release as a whole.

CONCLUSION: SUPPORTED
