**Question:** Does release 3.0 reduce p99 request latency?

**What each source shows**

- `sources/bench-a.md` reports that p99 fell from 180 ms to 144 ms, about 20%. p50 barely moved, 21 ms to 20 ms. The build tested was **3.0rc1**, the first release candidate, not the final release. The hardware was x86-64, and the run was on 2026-08-14.
- `sources/bench-b.md` reports p99 of 176 ms on 2.9.4 and 175 ms on 3.0, which it calls no change beyond run-to-run noise. p50 was 22 ms on both builds. The build tested was **3.0, the final release**. The hardware was ARM (aarch64), and the run was on 2026-09-09.

**Reconciliation**

The two sources do not directly contradict each other, because they differ in two ways:

1. **Build.** A tested a release candidate. B tested the final release. The question asks about release 3.0, so B matches it more closely. A is evidence about the rc only. Code could have changed between rc1 and the final build, but neither source says what changed.
2. **Architecture.** A used x86-64 and B used ARM. The improvement may be architecture-dependent, so it could be real on x86 and absent on ARM. The two benchmarks also gave different baselines for 2.9.4 (p99 of 180 ms on x86, 176 ms on ARM). Neither source tests the other architecture, so I can't separate the build effect from the hardware effect.

The workload, core count, memory and repetition count are the same in both. The benchmarks differ in who ran them, when, the build and the architecture.

**Where the evidence stops**

- No source tested the final 3.0 on x86-64, or 3.0rc1 on ARM. Those runs would show whether the build or the architecture explains the gap.
- Neither source gives variance, confidence intervals or per-run values. B asserts "noise" without a figure, and A reports a median of 5 runs without its spread.
- Neither source says what changed between 3.0rc1 and 3.0.
- Both sources describe a "parser rewrite" benchmark, but neither says whether the final release includes the same rewrite.

The sources show a p99 reduction only for the release candidate on x86-64. For the final release, the only evidence is a no-change result on ARM. They can't settle whether 3.0 reduces p99 latency in general.

CONCLUSION: UNRESOLVED
