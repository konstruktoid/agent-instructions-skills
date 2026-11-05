Yes. All three sources show release 4.2 raising the cache hit ratio above 90 percent, and each one does it with a different kind of comparison.

| Source | Setup | 4.1 | 4.2 |
|---|---|---|---|
| `sources/ops-weekly.md` | Production, week 37 vs week 38, with 4.2 deployed on 2026-09-14 | 71% | 93% |
| `sources/staging-replay.md` | Identical recorded traffic on identical hardware, one hour each | 70% | 92% |
| `sources/canary-log.md` | 10% of production traffic on 4.2 for 24 hours, the rest on 4.1 | 72% | 94% |

- **Production (`ops-weekly.md`):** The ratio rose from 71% to 93% across the deploy, with seven days of traffic on each side. The report says the only cache change between the two weeks was the key normalization in 4.2. This comparison is before and after, so it does not rule out a traffic shift between the weeks. The other two sources cover that gap.
- **Staging replay (`staging-replay.md`):** The same traffic ran on both releases, so traffic mix can't explain the gain. It reports that the release was the only difference between the deployments. It is a one-hour replay in staging, not production.
- **Canary (`canary-log.md`):** The 4.2 and 4.1 groups ran at the same time in production and received the same mix of requests. That controls for time and traffic. The window was 24 hours, and the canary group was 10% of traffic.

The three setups have different weaknesses, and they agree on the size of the gain. It is about 21 to 22 points each time (22 in the weekly report, 22 in the replay, 22 in the canary). The 4.2 figures are 92 to 94%, so the result clears 90% in every source. Together they point to the release as the cause.

Where the evidence stops:
- The sources only report point values, with no variance or confidence intervals. The margin over 90% is 2 to 4 points.
- The staging replay and canary windows are short, one hour and 24 hours. Only the weekly report covers a full week.
- The sources don't say whether the 90% mark holds under other traffic patterns or over a longer period.

CONCLUSION: SUPPORTED
