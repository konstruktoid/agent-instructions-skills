**Finding: the sources conflict, and the evidence for the final 3.0 release does not show a p99 reduction.**

**Benchmark A (`sources/bench-a.md`)**
- It tested 3.0rc1, a release candidate, not the final release.
- It ran on x86-64.
- p99 fell from 180 ms (2.9.4) to 144 ms (3.0rc1), about 20%. p50 was roughly flat, at 21 ms and 20 ms.
- Its method was 5 repetitions with the median reported, replaying production traffic at 400 requests per second.

**Benchmark B (`sources/bench-b.md`)**
- It tested 3.0, the final release.
- It ran on ARM (aarch64).
- p99 went from 176 ms (2.9.4) to 175 ms (3.0). p50 was 22 ms for both. The source says this is within run-to-run noise.
- Its method matched A: 5 repetitions with the median reported, and the same workload.

**Reconciliation**
- The two benchmarks differ in two ways: the build (release candidate vs. final) and the hardware (x86-64 vs. ARM). The sources don't say which of these caused the different results.
- A tested a build that isn't the one named in the question, so it is indirect evidence for "release 3.0". B tested the actual release and found no reduction.
- The 2.9.4 baselines are similar (180 ms vs. 176 ms). That suggests the difference lies in the 3.0 builds or the hardware, not in the baseline or workload.
- If the rc1 improvement was real, it may have been lost or reverted before the final release. Or it may only appear on x86-64. Neither source tests either explanation.

**Where the evidence stops**
- No source measures the final 3.0 on x86-64, so a hardware-specific gain can't be ruled in or out.
- No source measures rc1 on ARM, and neither reports variance or confidence intervals. "Within noise" in B is the source's own claim, without data.
- Nothing here covers other workloads or request rates.

**Conclusion:** The only evidence on the actual 3.0 release (B) shows no p99 change, on ARM. The positive result (A) comes from a different build on different hardware. The sources therefore don't establish a p99 reduction for 3.0. They also don't rule one out on x86-64, so the question can't be settled from them.

CONCLUSION: UNRESOLVED
