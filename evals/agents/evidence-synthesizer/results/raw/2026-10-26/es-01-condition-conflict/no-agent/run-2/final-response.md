Release 3.0 may reduce p99 latency on x86-64, but it did not on ARM. The two sources disagree, and they differ in both build and hardware, so I can't say which result applies to your deployment.

**What each source shows**
- **`sources/bench-a.md`:**
  - Build tested: 3.0rc1, a release candidate, not the final release.
  - Hardware: x86-64.
  - Result: p99 fell from 180 ms to 144 ms against 2.9.4, which the source calls a 20% drop. p50 moved from 21 ms to 20 ms.
- **`sources/bench-b.md`:**
  - Build tested: 3.0, the final release.
  - Hardware: ARM (aarch64).
  - Result: p99 went from 176 ms to 175 ms against 2.9.4, which the source calls within run-to-run noise. p50 stayed at 22 ms.

**What the two have in common**
- Both used a replay of ten minutes of production traffic at 400 requests per second.
- Both used 16 cores, 64 GB and 5 repetitions, reporting the median.
- Both compare against 2.9.4.
- The 2.9.4 baselines are close (180 ms and 176 ms), so the baseline doesn't explain the gap.

**Where the evidence stops**
- **Build and architecture are confounded.**
  - Bench A tests the release candidate on x86-64. Bench B tests the final release on ARM.
  - The data can't separate two explanations. The final 3.0 may have lost the improvement that 3.0rc1 had. Or the parser rewrite may help on x86-64 and not on ARM.
  - Only a run of the final 3.0 on x86-64, or of 3.0rc1 on ARM, would separate them.
- **Bench A doesn't test the release.** It measured 3.0rc1, so it is indirect evidence about 3.0 at best.
- **The noise level is unknown.** Both sources report medians of 5 runs, with no spread or confidence interval. Bench B calls its result noise without giving a number, and Bench A doesn't say how its 36 ms drop compares with run-to-run variation.
- **Bench B doesn't rule out an effect on x86-64.** It only shows no change on ARM.
- **Nothing here speaks to other conditions.** Neither source covers other hardware, load levels or workloads.

The only measurement of the final 3.0 shows no p99 change, and the improvement was seen only on a pre-release build and a different architecture. So the claim isn't established. The sources also don't contradict it for every environment.

CONCLUSION: UNRESOLVED
