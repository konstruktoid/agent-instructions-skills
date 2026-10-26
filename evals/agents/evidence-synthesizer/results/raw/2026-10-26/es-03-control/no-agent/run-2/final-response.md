Yes. All three sources show release 4.2 with a cache hit ratio above 90 percent, and each one also shows 4.1 well below that.

| Source | Setup | 4.1 | 4.2 |
|---|---|---|---|
| `sources/ops-weekly.md` | Production, week 37 against week 38, seven days each | 71% | 93% |
| `sources/staging-replay.md` | Same recorded traffic on identical hardware, one hour each | 70% | 92% |
| `sources/canary-log.md` | 10% canary against a 4.1 control, 24 hours, same request mix | 72% | 94% |

**Why the sources support the claim**
- **Production (`ops-weekly.md`):** 4.2 reached 93% after deploying on 2026-09-14, up from 71%. The report says the only cache change between the two weeks was the key normalization in 4.2.
- **Staging (`staging-replay.md`):** Identical traffic and hardware gave 92% for 4.2 against 70% for 4.1. The release was the only difference, which points to 4.2 itself as the cause.
- **Canary (`canary-log.md`):** The canary and control ran at the same time on the same mix of requests, so time and traffic differences are controlled. 4.2 reached 94% against 72% for 4.1.

Each source controls for something different: the week-over-week comparison does not, while the replay and the canary hold traffic and timing constant. All three give a rise of about 22 points, so the result is consistent.

**Where the evidence stops**
- **Cause:** The sources support "4.2 raised the ratio." Only `ops-weekly.md` names a mechanism, key normalization, and it does so as an assertion without a breakdown. The other two sources do not say why.
- **Margin:** The staging figure of 92% is the closest to the 90% line, about 2 points above it. It comes from a single one-hour run, and the sources give no variance or confidence intervals.
- **Duration:** The canary covers 24 hours and the staging replay one hour. Only the production report covers a full week.

CONCLUSION: SUPPORTED
