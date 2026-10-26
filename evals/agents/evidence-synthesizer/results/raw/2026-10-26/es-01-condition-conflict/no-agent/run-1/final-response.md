**Finding: the two sources disagree, and the question is unresolved.**

**What each source shows**
- `sources/bench-a.md`: p99 fell from 180 ms on 2.9.4 to 144 ms on 3.0rc1, which is 20% lower. The build tested was the first release candidate, not the final release. It ran on x86-64 on 2026-08-14 and the platform team ran it.
- `sources/bench-b.md`: p99 went from 176 ms on 2.9.4 to 175 ms on 3.0, a change the source calls "did not change beyond run-to-run noise". The build tested was the final 3.0 release. It ran on ARM (aarch64) on 2026-09-09 and the release team ran it.

**Where they match**
Both sources use the same workload: ten minutes of replayed production traffic at 400 requests per second. Both use 16 cores, 64 GB of memory, and 5 repetitions with the median reported. Both use 2.9.4 as the baseline. Their 2.9.4 baselines are close (180 ms and 176 ms).

**Why I can't reconcile them**
- Only `bench-b.md` tested the final 3.0 release, and it found no p99 improvement. `bench-a.md` tested a release candidate, so its 20% gain may not carry over to the final build. The sources don't say what changed between 3.0rc1 and 3.0.
- The hardware differs (x86-64 against ARM). The gain could be specific to x86-64, but neither source tests that. Each source varies build and architecture together, so the data can't separate the two causes.
- Neither source gives run-to-run variance or the individual repetitions. I can't judge how large the noise is, or whether the 36 ms drop in `bench-a.md` is outside it. `bench-b.md` asserts noise without showing numbers.

**Where the evidence stops**
- `bench-a.md` supports a p99 reduction for 3.0rc1 on x86-64. It doesn't establish that for release 3.0.
- `bench-b.md` shows no p99 reduction for release 3.0 on ARM. It doesn't test x86-64.
- Neither source tests the final 3.0 on x86-64, or 3.0rc1 on ARM. Those runs would settle whether the difference comes from the build or the hardware.

The sources neither establish the reduction nor rule it out. The only data on the final release shows no change, and the one reported gain comes from a different build on different hardware.

CONCLUSION: UNRESOLVED
