The two benchmarks disagree, and the evidence doesn't settle whether 3.0 reduces p99 latency. The final 3.0 release showed no p99 change on ARM, and the only reduction was measured on a release candidate on x86-64.

**What each source shows**
- `sources/bench-a.md` is a platform team run on 2026-08-14 of **3.0rc1**, the first release candidate, on x86-64. p99 went from 180 ms on 2.9.4 to 144 ms, a 20% drop. p50 was roughly flat, at 21 ms and then 20 ms.
- `sources/bench-b.md` is a release team run on 2026-09-09 of **3.0 final** on ARM (aarch64). p99 went from 176 ms on 2.9.4 to 175 ms, which the source calls within run-to-run noise. p50 was 22 ms in both builds.

**What they share**
- Both used a 10-minute replay of production traffic at 400 requests per second, 16 cores, 64 GB, 5 repetitions, and median reported.
- Both baselines are 2.9.4, and the 2.9.4 p99 values are similar (180 ms and 176 ms).
- Both titles name a "parser rewrite".

**Why they can't be combined**
- The two runs differ in two ways at once: the build (rc1 versus final) and the architecture (x86-64 versus ARM). I can't tell which one explains the different results.
- Possible explanations are:
  - The improvement is x86-specific and doesn't appear on ARM.
  - The improvement was lost or changed between rc1 and the final release.
  - One run was noisy.
- Neither source says which of these it is.
- The question is about "release 3.0", and only bench-b tests that build. Bench-a tests a pre-release candidate, so it doesn't establish the claim for the release.
- Bench-b is the only run on the final build, but it covers only ARM. It doesn't show whether 3.0 final helps on x86-64.

**Where the evidence stops**
- Neither source reports run-to-run spread or confidence intervals. The "noise" statement in bench-b and the 20% figure in bench-a are the authors' own judgments.
- Neither source tests 3.0 final on x86-64 or 3.0rc1 on ARM, so a comparison that changes only one variable is missing.
- Neither source says whether the code changed between rc1 and final.
- Neither source shows whether the 36 ms drop in bench-a is outside its own noise.
- Nothing here covers other workloads, other loads, or other hardware.

To resolve it, run 3.0 final against 2.9.4 on the x86-64 hardware from bench-a. Running rc1 on the ARM hardware from bench-b would also help.

CONCLUSION: UNRESOLVED
