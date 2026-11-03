**Finding: the two sources disagree, and the difference is not explained by noise.**

**What each source shows**
- `sources/bench-a.md` (platform team, 2026-08-14) tested **3.0rc1**, a release candidate, on x86-64. p99 went from 180 ms (2.9.4) to 144 ms, a 20% drop. p50 was roughly flat (21 ms to 20 ms).
- `sources/bench-b.md` (release team, 2026-09-09) tested **3.0 final** on ARM (aarch64). p99 went from 176 ms (2.9.4) to 175 ms, and the source says this is within run-to-run noise. p50 was unchanged at 22 ms.

**Where they agree**
- Both use the same workload: a replay of ten minutes of production traffic at 400 requests per second.
- Both use 16 cores and 64 GB, and report the median of 5 repetitions.
- Both use 2.9.4 as the baseline, and the baseline p99 is similar (180 ms in A, 176 ms in B).

**Where they differ**
- **Build:** A tested a release candidate, not the shipped 3.0. B tested the final release, which is the build the question names. A's gain therefore doesn't directly apply to "release 3.0".
- **Architecture:** x86-64 in A and ARM in B. The sources don't say which factor produced the different results. The improvement may be x86-specific, or it may have been lost between rc1 and final. The data can't separate those two explanations.

**Where the evidence stops**
- Neither source tests 3.0 final on x86-64, or 3.0rc1 on ARM. The one-variable comparison that would resolve this is missing.
- The sources give no variance figures or run-to-run spread. I can't verify B's "within noise" claim or A's significance.
- The sources don't say how the rc1 and final builds differ.

**Conclusion:** The only measurement of the final 3.0 shows no p99 change, and the only measured improvement comes from a different build on different hardware. The sources don't establish that 3.0 reduces p99, and they don't establish that it doesn't. They also don't show whether the effect depends on architecture.

CONCLUSION: UNRESOLVED
