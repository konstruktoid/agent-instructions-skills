**Conclusion: the two sources disagree, and the difference in what they tested leaves the question open.**

**What each source shows**
- `sources/bench-a.md` tested **3.0rc1**, the first release candidate, not the final release. It ran on x86-64.
  - p99 went from 180 ms (2.9.4) to 144 ms (3.0rc1), which the source calls a 20% drop.
  - p50 went from 21 ms to 20 ms.
- `sources/bench-b.md` tested **3.0, the final release**. It ran on aarch64.
  - p99 went from 176 ms (2.9.4) to 175 ms (3.0). The source says this is within run-to-run noise.
  - p50 was 22 ms for both builds.

**What the two have in common**
- Both used the same workload: a replay of ten minutes of production traffic at 400 requests per second.
- Both used 16 cores, 64 GB of memory, and 5 repetitions with the median reported.
- The 2.9.4 baselines agree: 180 ms in A and 176 ms in B.

**Why they can't be combined**
- Only `bench-b.md` tested the build the question asks about, and it shows no p99 improvement.
- `bench-a.md` shows an improvement, but on a release candidate. Nothing in the sources says the candidate's parser code matches the final release.
- The two runs also differ in CPU architecture, so the architecture could explain the gap instead of the build. The sources don't say which it is.
- Neither source gives run-to-run spread, so I can't check the "noise" claim in B or the size of A's gain.
- The runs were by different teams on different dates (2026-08-14 and 2026-09-09).

**Where the evidence stops**
- It does not establish that 3.0 reduces p99 on aarch64. B is the only test of the final build, and it found no change.
- It does not establish that 3.0 reduces p99 on x86-64. The only x86-64 run, A, used a release candidate.
- It does not show that the change from rc1 to final removed the gain, or that architecture is the cause. A run of the final 3.0 on x86-64 would settle this.

CONCLUSION: UNRESOLVED
