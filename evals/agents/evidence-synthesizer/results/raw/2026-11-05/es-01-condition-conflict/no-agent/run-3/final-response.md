Release 3.0 does not reduce p99 latency on the evidence available. The one benchmark that shows a reduction tested a release candidate, and the benchmark of the final release shows no change.

**What each source shows**
- `sources/bench-a.md` tested **3.0rc1**, not the final release, on x86-64. Median p99 went from 180 ms (2.9.4) to 144 ms, a 20% drop. p50 barely moved, 21 ms to 20 ms.
- `sources/bench-b.md` tested **3.0, the final release**, on ARM (aarch64). Median p99 went from 176 ms (2.9.4) to 175 ms, and p50 was unchanged at 22 ms. The source says this is within run-to-run noise.

**Reconciling them**
- The two benchmarks are not like for like. They differ in build (rc1 versus final), architecture (x86-64 versus ARM), date (2026-08-14 versus 2026-09-09) and team (platform versus release). The workload, core count, memory and repetition count are the same. The sources don't say which of these differences explains the gap.
- The question is about release 3.0, and only `bench-b.md` tests that build. It finds no effect.
- `bench-a.md` shows that the rc1 improved p99 on x86-64. It can't establish that for the final release. The sources don't say whether the parser rewrite changed between rc1 and final, and I haven't assumed it did.
- Two explanations fit the data: the improvement is specific to x86-64, or the final build lost the rc1 gain. Neither source can separate them.

**Where the evidence stops**
- Nothing tests the final 3.0 build on x86-64. Nothing tests rc1 on ARM.
- Neither source reports run-to-run variance. The "within noise" claim in `bench-b.md` is the authors' statement, with no spread given.
- Both use the same replayed production traffic at 400 requests per second. Neither says anything about other loads.

The only test of the actual release found no p99 reduction. The positive result comes from a pre-release build on different hardware. The sources therefore give no support for the claim as stated, and the one direct measurement contradicts it. They do leave open that 3.0 helps on x86-64. A final-build run on x86-64 would settle that.

CONCLUSION: UNSUPPORTED
