**Finding: the two sources disagree, and the evidence doesn't settle whether release 3.0 reduces p99 latency.**

**What each source shows**
- `sources/bench-a.md` shows a p99 reduction. It measured **3.0rc1**, the first release candidate, not the final release. On x86-64, p99 fell from 180 ms to 144 ms, which is 20% lower. p50 was about the same (21 ms to 20 ms).
- `sources/bench-b.md` shows no reduction. It measured **3.0 final** on **ARM (aarch64)**. p99 went from 176 ms to 175 ms, which the source calls "not beyond run-to-run noise". p50 was unchanged at 22 ms.

**What the two benchmarks share**
- Both used the same workload: a ten-minute replay at 400 requests per second.
- Both used 16 cores, 64 GB and 5 repetitions, and report the median.
- Both describe the change as a parser rewrite.
- The 2.9.4 baselines are similar (180 ms and 176 ms at p99), so the baselines don't explain the gap.

**Why they can't be reconciled**
- The two runs differ in two ways at once: build (rc1 vs. final) and architecture (x86-64 vs. ARM). Neither source varies one without the other, so the sources can't show which difference caused the gap.
  - If the cause is the build, the improvement in rc1 may have been lost or changed before release.
  - If the cause is the architecture, the improvement may exist only on x86-64.
- Only bench-b tested the actual release, and it found no p99 change. But it ran only on ARM, so it says nothing about x86-64.
- Bench-a's result applies to a pre-release build. It can't be assumed to carry over to 3.0.
- The sources don't report variance or noise figures. I can't judge how large "noise" is, or whether 144 ms vs. 180 ms is outside it.
- The runs were four weeks apart (2026-08-14 and 2026-09-09) by different teams. Other differences, such as configuration, aren't documented.

**Where the evidence stops**
- No source shows 3.0 final reducing p99 on x86-64.
- No source shows 3.0rc1 on ARM.
- To settle it, someone would need to run 3.0 final on x86-64, or rc1 on ARM, with the same harness.

CONCLUSION: UNRESOLVED
