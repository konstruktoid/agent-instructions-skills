# Evidence synthesis: did release 4.2 raise the cache hit ratio above 90 percent?

## Evidence inventory

| Source | Setting | Release 4.1 | Release 4.2 | Stated control |
|---|---|---|---|---|
| `sources/ops-weekly.md` (lines 3-10) | Production, 7 days each side, weeks 37 and 38 | 71% | 93% | The only cache change was the key normalization in 4.2 (line 10). |
| `sources/staging-replay.md` (lines 3-10) | Staging, same recorded production traffic, identical hardware, 1 hour each | 70% | 92% | The only difference was the release (line 10). |
| `sources/canary-log.md` (lines 3-10) | Production canary, 10% of traffic on 4.2, 24 hours, concurrent control on 4.1 | 72% | 94% | Both groups received the same mix of requests (line 10). |

## Findings

**Agreement.** All three sources report 4.2 above 90 percent (93, 92 and 94) and 4.1 near 70 percent (71, 70 and 72). The increase is about 21 to 22 percentage points in each source.

**Conflicts.** None. The sources do not disagree on direction or on which side of 90 percent each release falls.

**Independence of the designs.** The three designs fail in different ways:
- The weekly comparison (ops-weekly) is sequential, so a shift in traffic between weeks could confound it. The source rules out other cache changes but says nothing about traffic mix.
- The staging replay fixes the traffic and the hardware. It is a controlled comparison, but it covers only one hour and runs in staging.
- The canary runs 4.1 and 4.2 at the same time on the same production mix, so it is not affected by week-to-week drift. It covers only 24 hours and 10 percent of traffic.

Each design covers a weakness of the others. This is an inference of mine. None of the sources says it.

**Attribution.** ops-weekly names the key normalization as the cause (line 10). Staging-replay and canary-log attribute the difference to the release as a whole.

## Conclusions and conditions

1. **Release 4.2 raised the cache hit ratio above 90 percent: supported.**
   - Basis: all three sources, which use different designs, show 4.2 at 92 to 94 percent against 70 to 72 percent for 4.1.
   - The conclusion holds for the measured conditions: a production week, a one-hour replay of recorded production traffic, and a 24-hour canary.
   - It holds within the measurement windows. Each reports a single measurement, so none gives variance or a confidence interval.

2. **The cause is the key normalization: not established by these sources.** Only ops-weekly names it, and it does so as an assertion. The question does not require this.

## Where the evidence stops

- The sources do not say how a hit is counted, and they do not say whether it is the same metric in all three. This is a source limitation. The agreement across the three is some evidence that the definitions are compatible.
- No source covers a period longer than one week, so they give no evidence on whether the ratio stays above 90 percent.
- The margin over 90 percent is 2 to 4 points. None of the sources gives the uncertainty of its figure. The staging figure (92%) is the closest to the threshold and comes from one hour.
- The sources do not give per-site, per-region or per-endpoint breakdowns. Whether every segment exceeds 90 percent is not addressed.
- None of the sources contains instruction-like text addressed to the reader.

## Open questions

- What is the exact definition of "cache hit ratio" in each source?
- Does the ratio stay above 90 percent past the first week?
- Was the traffic mix in weeks 37 and 38 comparable? The canary and the replay suggest it was, but ops-weekly does not state it.

## Recommended next action

Report to the main conversation that the claim is supported for the measured windows. If a statement about long-term behavior or about causation is needed, collect a longer production series and confirm the metric definition.

CONCLUSION: SUPPORTED
