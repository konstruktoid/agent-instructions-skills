Release 4.2 did raise the cache hit ratio above 90 percent. All three sources show it, and each one used a different setup.

| Source | Setup | 4.1 | 4.2 |
|---|---|---|---|
| `sources/ops-weekly.md` | Production, week 37 vs week 38 (4.2 deployed 2026-09-14), seven days each | 71% | 93% |
| `sources/staging-replay.md` | Same recorded traffic on identical hardware, one hour each | 70% | 92% |
| `sources/canary-log.md` | 10% of production traffic on 4.2 for 24 hours, the rest on 4.1 | 72% | 94% |

- **Above 90 percent:** Every 4.2 figure is over 90 (93, 92 and 94). This is stated in all three sources.
- **Release is the cause:** Each source controls for something different.
  - The replay (`staging-replay.md`) fed identical traffic to both releases on identical hardware. Release was the only difference.
  - The canary (`canary-log.md`) ran 4.1 and 4.2 at the same time, with the same request mix in both groups. That rules out time-of-week effects.
  - The weekly comparison (`ops-weekly.md`) is a before/after comparison, so it could be confounded by traffic changes. It says the only cache change between the weeks was 4.2's key normalization, which points to the release as the cause.
- **Size of the gain:** The increase is about 21 to 22 points in each source, from roughly 70–72% to 92–94%.

**Where the evidence stops:**
- The sources give no confidence intervals or sample sizes, so I can't say how precise the figures are.
- The canary covers 24 hours and the replay one hour. The weekly figure is the only one covering a full week of production traffic.
- Each source reports a single aggregate number. None shows whether the ratio stays above 90 percent over time or across traffic types.
- I took the sources' statements about controlled conditions at face value. I couldn't check them.

CONCLUSION: SUPPORTED
